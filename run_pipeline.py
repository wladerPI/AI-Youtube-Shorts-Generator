# run_pipeline.py
"""
=============================================================================
PIPELINE PRINCIPAL — LIVE → SHORTS VIRAIS
=============================================================================

⚠️ PROBLEMAS ATUAIS DO PIPELINE:

1. FILTROS MUITO AGRESSIVOS
   - _deduplicate_segments com min_gap=60s mata muitos clips
   - filter_by_time_distance também muito restritivo
   - Resultado: 544 highlights → 4 shorts finais ❌

2. PROCESSAMENTO SEQUENCIAL LENTO
   - Processa 1 clip por vez
   - Live de 5h demora ~2-3 horas para processar

3. SEM FEEDBACK DO USUÁRIO
   - Gera todos os shorts sem mostrar prévia

4. DEPENDÊNCIA CRÍTICA DO GPT
   - Se GPT falhar, todo pipeline falha

🔧 MELHORIAS PRIORITÁRIAS:

CURTO PRAZO:
1. Remover/relaxar filtros agressivos
2. Adicionar logs detalhados
3. Implementar modo preview

MÉDIO PRAZO:
1. Paralelizar processamento
2. Adicionar checkpoint/resume
3. Cache de transcrições

LONGO PRAZO:
1. Análise de áudio sem GPT
2. Sistema de ML para preferências
3. Dashboard com métricas

=============================================================================
"""

import sys
import os
import uuid
import re
import json

PIPELINE_MODE = "LIVE"
DRY_RUN = False
USE_LLM_SELECTION = True

print("🚨 PIPELINE EXECUTANDO 🚨")
print("=" * 60)

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
    """Limpa nome de arquivo."""
    name = name.lower()
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '-', name)
    return name[:80]


def _deduplicate_segments(segments, min_gap=60):
    """
    ⚠️ PROBLEMA CRÍTICO: min_gap=60s é MUITO RESTRITIVO!
    
    SOLUÇÃO SUGERIDA: Reduzir para 20-30s ou remover completamente
    """
    if not segments:
        return []
    
    segs = sorted(segments, key=lambda s: float(s["start"]))
    out = [segs[0]]
    
    for s in segs[1:]:
        last = out[-1]
        last_end = float(last["end"])
        s_start = float(s["start"])
        
        if s_start < last_end:
            continue
        
        if s_start - last_end < min_gap:
            continue  # ← AQUI que mata 90% dos clips!
        
        out.append(s)
    
    return out


def main():
    """Função principal do pipeline."""
    
    if len(sys.argv) < 2:
        print("❌ Uso: python run_pipeline.py input\\video.mp4")
        sys.exit(1)

    input_video = sys.argv[1]
    if not os.path.isfile(input_video):
        print("❌ Vídeo não encontrado")
        sys.exit(1)

    os.makedirs("clips", exist_ok=True)
    os.makedirs("shorts", exist_ok=True)
    os.makedirs("rankings", exist_ok=True)
    os.makedirs("input", exist_ok=True)

    session = str(uuid.uuid4())[:8]
    base_name = clean_filename(os.path.splitext(os.path.basename(input_video))[0])
    audio_file = f"audio_{session}.wav"

    # ETAPA 1: Extrair áudio
    print("🎧 Extraindo áudio...")
    extractAudio(input_video, audio_file)

    # ETAPA 2: Transcrever
    print("🧠 Transcrevendo...")
    transcriptions = transcribeAudio(audio_file)
    
    if not transcriptions:
        print("❌ Transcrição vazia")
        return

    video_duration = max(t[2] for t in transcriptions) if transcriptions else 0
    video_duration_min = video_duration / 60
    print(f"📊 Vídeo: {video_duration_min:.1f} minutos ({video_duration:.0f}s)")

    # ETAPA 3: Selecionar segmentos
    print("🧠 Selecionando segmentos (rizadas, memes, rage)...")
    segments = select_segments_with_llm(
        transcriptions,
        max_segments=MAX_SHORTS,
        min_duration=45,
        max_duration=180,
        prefer_llm=USE_LLM_SELECTION,
        video_duration_min=video_duration_min
    )

    print(f"📌 Segmentos brutos encontrados: {len(segments)}")

    # ETAPA 4: Filtros (PROBLEMA: muito agressivos!)
    segments = _deduplicate_segments(segments, min_gap=60)
    print(f"📌 Após deduplicação: {len(segments)}")
    
    segments = filter_by_time_distance(segments, min_distance=60)
    print(f"📌 Após filtro temporal: {len(segments)}")
    
    segments = segments[:MAX_SHORTS]
    print(f"📌 Segmentos finais: {len(segments)}")

    if not segments:
        print("❌ Nenhum segmento selecionado")
        return

    ranking = []

    # ETAPA 5: Processar cada segmento
    for idx, seg in enumerate(segments, 1):
        start = float(seg["start"])
        end = float(seg["end"])
        duration = end - start

        if duration < 30:
            continue

        reason = seg.get("reason", "sem motivo")
        print(f"\n🎬 Clip {idx}/{len(segments)}: {start:.1f}s → {end:.1f}s ({duration:.1f}s)")
        print(f"   💡 Motivo: {reason}")

        clip_path = f"clips/{base_name}_{idx}_{session}.mp4"
        short_path = f"shorts/{base_name}_SHORT_{idx}_{session}.mp4"
        temp_silence_path = clip_path.replace(".mp4", "_nosilence.mp4")

        if not DRY_RUN:
            crop_video(input_video, clip_path, start, end)
            remove_silence(video_in=clip_path, video_out=temp_silence_path)
            render_vertical_video(temp_silence_path, short_path, pan_engine=True)
            
            if os.path.exists(temp_silence_path):
                try:
                    os.remove(temp_silence_path)
                except Exception:
                    pass

        viral = calculate_viral_score(start, end, reason)
        curve = build_attention_curve(audio_file, duration)
        retention = calculate_retention_metrics(curve)

        score = calculate_rank_score({
            "viral_score": viral,
            "retention_score": retention["score"],
            "duration": duration,
            "drop_risk": retention.get("drop_risk", "medio")
        })

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
            "duration": duration,
            "reason": reason,
            "viral": viral,
            "retention": retention["score"],
            "rank": score
        })

    ranking_sorted = sorted(ranking, key=lambda x: x["rank"], reverse=True)
    
    with open("rankings/ranking.json", "w", encoding="utf-8") as f:
        json.dump(ranking_sorted, f, indent=2, ensure_ascii=False)

    if os.path.exists(audio_file):
        os.remove(audio_file)

    print("\n" + "=" * 60)
    print("🎉 PIPELINE FINALIZADO 🎉")
    print(f"   📊 {len(ranking)} shorts gerados em shorts/")
    if ranking_sorted:
        print(f"   🏆 Top 3 por ranking:")
        for i, r in enumerate(ranking_sorted[:3], 1):
            print(f"      {i}. {r['file'].split('/')[-1]} - Score: {r['rank']:.2f}")
    print("=" * 60)


if __name__ == "__main__":
    main()

"""
ROADMAP DE MELHORIAS:

🔴 CRÍTICO:
1. Resolver filtros agressivos
2. Melhorar consistência do GPT
3. Adicionar logging detalhado

🟡 IMPORTANTE:
1. Cachear transcrições
2. Paralelizar renderização
3. Modo preview

🟢 DESEJÁVEL:
1. UI web
2. Análise de áudio sem GPT
3. Sistema de aprendizado

🔵 FUTURO:
1. Múltiplas línguas
2. Detecção de rostos
3. Upload automático
"""
