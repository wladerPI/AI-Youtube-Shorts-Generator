# run_pipeline.py
"""
=============================================================================
PIPELINE PRINCIPAL — LIVE → SHORTS VIRAIS
=============================================================================
CONTEXTO: Leia PROJECT_OVERVIEW.md para visão geral do projeto.

O QUE FAZ:
  Orquestra todo o processo de transformação de uma live em múltiplos shorts:
  1. Extrai áudio
  2. Transcreve com Whisper
  3. Seleciona segmentos via LLM (rizadas, memes, rage) ou heurística
  4. Remove silêncios
  5. Renderiza vertical COM ÁUDIO + pan para memes nos cantos
  6. Gera legendas SRT
  7. Salva ranking.json

COMO EXECUTAR:
  python run_pipeline.py input\\video.mp4

ALTERAÇÕES REALIZADAS:
  - Troca de AISegmentSelector (heurístico) para SegmentSelectorLLM (GPT)
  - Adição de _deduplicate_segments (evita Clip 1 e 5 serem iguais)
  - VerticalCropper passou a usar MoviePy (preserva áudio)
  - Duração de segmentos: 30s a 3min (contexto completo)
  - Mais shorts por live: LIVE=25, INSANO=35

O QUE AINDA PODE SER FEITO:
  - Processar múltiplos vídeos em batch
  - Modo interativo para aprovar/rejeitar segmentos
  - Salvar progresso para retomada após falha
  - Estimativa de tempo restante
=============================================================================
"""

import sys
import os
import uuid
import re
import json

# ---------------------------------------------------------------------------
# CONFIGURAÇÕES DO PIPELINE
# ---------------------------------------------------------------------------
# LIVE = produção normal | TEST = poucos shorts para teste | INSANO = máximo
PIPELINE_MODE = "LIVE"

# Se True, não renderiza vídeos (apenas simula)
DRY_RUN = False

# True = usa GPT para detectar rizadas/memes | False = heurística (sem API)
USE_LLM_SELECTION = True

print("🚨 PIPELINE EXECUTANDO 🚨")
print("=" * 60)

# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
from Components.Edit import extractAudio, crop_video
from Components.Transcription import transcribeAudio
from Components.EtapaJ_RemoveSilence import remove_silence
from Components.SegmentSelectorLLM import select_segments_with_llm
from Components.TemporalFilter import filter_by_time_distance
from Components.ViralScore import calculate_viral_score
from Components.AttentionCurve import build_attention_curve
from Components.RetentionScore import calculate_retention_metrics
from Components.SmartRanking import calculate_rank_score
from Components.SubtitleGenerator import generate_srt
from Render.VerticalCropper import render_vertical_video
from Components.PipelineConfig import get_pipeline_config

config = get_pipeline_config(PIPELINE_MODE)
MAX_SHORTS = config["MAX_SHORTS"]
MIN_RETENTION = config["MIN_RETENTION"]
MIN_VIRAL = config["MIN_VIRAL"]


def clean_filename(name):
    """
    Limpa nome de arquivo: minúsculo, sem caracteres inválidos, hífens no lugar de espaços.
    Necessário para nomes compatíveis com Windows/Linux.
    """
    name = name.lower()
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '-', name)
    return name[:80]


def _deduplicate_segments(segments, min_gap=90):
    """
    Remove segmentos sobrepostos ou muito próximos no tempo.
    
    POR QUE: Em execuções anteriores, Clip 1 e Clip 5 eram o mesmo segmento
    (5129s-5170s). A deduplicação evita shorts repetidos.
    
    min_gap: distância mínima em segundos entre o fim de um e o início do próximo.
    """
    if not segments:
        return []
    segs = sorted(segments, key=lambda s: float(s["start"]))
    out = [segs[0]]
    for s in segs[1:]:
        last = out[-1]
        last_end = float(last["end"])
        s_start = float(s["start"])
        # Ignora se sobrepõe
        if s_start < last_end:
            continue
        # Ignora se está muito próximo
        if s_start - last_end < min_gap:
            continue
        out.append(s)
    return out


def main():
    # Validar argumentos
    if len(sys.argv) < 2:
        print("❌ Uso: python run_pipeline.py input\\video.mp4")
        sys.exit(1)

    input_video = sys.argv[1]
    if not os.path.isfile(input_video):
        print("❌ Vídeo não encontrado")
        sys.exit(1)

    # Criar pastas de saída
    os.makedirs("clips", exist_ok=True)
    os.makedirs("shorts", exist_ok=True)
    os.makedirs("rankings", exist_ok=True)
    os.makedirs("input", exist_ok=True)

    # ID único da sessão (permite múltiplas execuções simultâneas)
    session = str(uuid.uuid4())[:8]
    base_name = clean_filename(os.path.splitext(os.path.basename(input_video))[0])
    audio_file = f"audio_{session}.wav"

    # ETAPA 1: Extrair áudio (necessário para transcrição)
    print("🎧 Extraindo áudio...")
    extractAudio(input_video, audio_file)

    # ETAPA 2: Transcrever (Whisper retorna palavra + timestamp)
    print("🧠 Transcrevendo...")
    transcriptions = transcribeAudio(audio_file)
    if not transcriptions:
        print("❌ Transcrição vazia")
        return

    # Duração estimada do vídeo (para o LLM saber quantos momentos pedir)
    video_duration = max(t[2] for t in transcriptions) if transcriptions else 0
    video_duration_min = video_duration / 60

    # ETAPA 3: Selecionar segmentos (LLM ou heurística)
    print("🧠 Selecionando segmentos (rizadas, memes, rage)...")
    segments = select_segments_with_llm(
        transcriptions,
        max_segments=MAX_SHORTS,
        min_duration=30,   # Shorts de no mínimo 30s (contexto)
        max_duration=180,  # Até 3min (usuário ajusta no CapCut)
        prefer_llm=USE_LLM_SELECTION,
        video_duration_min=video_duration_min
    )

    # Deduplicar e filtrar por distância temporal
    segments = _deduplicate_segments(segments, min_gap=90)
    segments = filter_by_time_distance(segments, min_distance=90)
    segments = segments[:MAX_SHORTS]

    if not segments:
        print("❌ Nenhum segmento selecionado")
        return

    ranking = []

    # ETAPA 4: Processar cada segmento
    for idx, seg in enumerate(segments, 1):
        start = float(seg["start"])
        end = float(seg["end"])
        duration = end - start

        if duration < 15:
            continue

        print(f"🎬 Clip {idx}: {start:.1f}s → {end:.1f}s ({duration:.1f}s)")

        clip_path = f"clips/{base_name}_{idx}_{session}.mp4"
        short_path = f"shorts/{base_name}_SHORT_{idx}_{session}.mp4"
        temp_silence_path = clip_path.replace(".mp4", "_nosilence.mp4")

        if not DRY_RUN:
            # Cortar trecho do vídeo original
            crop_video(input_video, clip_path, start, end)
            # Remover silêncios longos (reduz duração)
            remove_silence(
                video_in=clip_path,
                video_out=temp_silence_path
            )
            # Renderizar vertical COM ÁUDIO + pan para memes
            render_vertical_video(
                temp_silence_path,
                short_path,
                pan_engine=True
            )
            # Limpar arquivo temporário
            if os.path.exists(temp_silence_path):
                try:
                    os.remove(temp_silence_path)
                except Exception:
                    pass

        # Calcular scores para ranking
        viral = calculate_viral_score(start, end, seg.get("reason", ""))
        curve = build_attention_curve(audio_file, duration)
        retention = calculate_retention_metrics(curve)

        score = calculate_rank_score({
            "viral_score": viral,
            "retention_score": retention["score"],
            "duration": duration,
            "drop_risk": retention.get("drop_risk", "medio")
        })

        # Gerar legendas SRT
        generate_srt(
            transcriptions,
            clip_start=start,
            clip_end=end,
            output_path=short_path.replace(".mp4", ".srt")
        )

        ranking.append({
            "file": short_path,
            "start": start,
            "end": end,
            "viral": viral,
            "retention": retention["score"],
            "rank": score
        })

    # Salvar ranking final
    with open("rankings/ranking.json", "w", encoding="utf-8") as f:
        json.dump(ranking, f, indent=2, ensure_ascii=False)

    # Limpar áudio temporário
    if os.path.exists(audio_file):
        os.remove(audio_file)

    print("🔥 PIPELINE FINALIZADO 🔥")
    print(f"   {len(ranking)} shorts gerados em shorts/")


if __name__ == "__main__":
    main()
