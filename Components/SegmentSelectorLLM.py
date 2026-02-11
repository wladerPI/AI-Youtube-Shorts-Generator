# Components/SegmentSelectorLLM.py
"""
=============================================================================
SELETOR DE SEGMENTOS COM LLM (GPT)
=============================================================================

O QUE FAZ:
  Seleciona os melhores momentos da live usando GPT. Prioriza:
  - Rizadas (momentos de risada)
  - Memes
  - Rage, humor, reações exageradas
  Usa merge_coherent_segments para expandir e manter contexto completo
  (não corta frases no meio). Deduplica segmentos sobrepostos.

ALTERAÇÕES (em relação ao AISegmentSelector heurístico):
  - Novo componente criado para usar LLM
  - Permite shorts de 30s a 3min (antes 10-90s)
  - Fallback para AISegmentSelector quando sem API key

O QUE AINDA PODE SER FEITO:
  - Fine-tune do prompt por canal
  - Usar modelo local (Ollama) como alternativa
  - Cache de highlights para reprocessamento
=============================================================================
"""

import json
import re
import os
from dotenv import load_dotenv
load_dotenv()

from Components.LanguageTasks import GetHighlights
from Components.EtapaG_CoherentSegments import merge_coherent_segments


def _build_transcript_with_timestamps(transcriptions, interval_sec=15):
    """
    Converte [(palavra, start, end), ...] em texto com timestamps [MM:SS].
    O LLM precisa dos timestamps para retornar setup_start e reaction_end.
    Agrupa palavras em blocos de ~interval_sec segundos.
    """
    if not transcriptions:
        return ""

    lines = []
    current_time = 0
    current_words = []

    for word, start, end in transcriptions:
        # Novo bloco quando ultrapassar o intervalo
        if start >= current_time + interval_sec and current_words:
            ts = int(current_time)
            lines.append(f"[{ts//60}:{ts%60:02d}] {' '.join(current_words)}")
            current_time = int(start / interval_sec) * interval_sec
            current_words = []

        current_words.append(word)

    if current_words:
        ts = int(current_time)
        lines.append(f"[{ts//60}:{ts%60:02d}] {' '.join(current_words)}")

    return "\n".join(lines)


def select_segments_with_llm(
    transcriptions,
    max_segments=25,
    min_duration=30,
    max_duration=180,
    prefer_llm=True,
    video_duration_min=240
):
    """
    Fluxo: GetHighlights (LLM) → merge_coherent_segments → deduplicate.
    Se prefer_llm=False ou sem API key → usa fallback heurístico.
    """
    transcript_text = _build_transcript_with_timestamps(transcriptions, interval_sec=20)

    if not transcript_text.strip():
        return []

    if prefer_llm and (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API")):
        try:
            highlights = GetHighlights(transcript_text, video_duration_min=video_duration_min)
            if highlights:
                segments = merge_coherent_segments(
                    transcriptions,
                    highlights,
                    min_duration=min_duration,
                    max_duration=max_duration,
                    gap_tolerance=2.0,   # Até 2s de gap = mesma frase
                    context_padding=3.0  # Margem para contexto
                )
                return _deduplicate_segments(segments[:max_segments])
        except Exception as e:
            print(f"⚠️ LLM falhou ({e}) — usando fallback heurístico")

    return _fallback_heuristic(transcriptions, max_segments, min_duration, max_duration)


def _deduplicate_segments(segments, min_gap_sec=60):
    """
    Remove sobreposições. Se dois segmentos se sobrepõem, mantém o de maior score.
    Ignora segmentos muito próximos (< min_gap_sec).
    """
    if not segments:
        return []

    segments = sorted(segments, key=lambda s: s["start"])
    result = [segments[0]]

    for seg in segments[1:]:
        last = result[-1]
        overlap = seg["start"] < last["end"]
        too_close = (seg["start"] - last["end"]) < min_gap_sec

        if overlap:
            if seg.get("score", 0) > last.get("score", 0):
                result[-1] = seg
            continue

        if too_close:
            continue

        result.append(seg)

    return result


def _fallback_heuristic(transcriptions, max_seg, min_dur, max_dur):
    """Usa AISegmentSelector (palavras-chave, densidade) quando LLM indisponível."""
    from Components.AISegmentSelector import select_best_segments

    raw = select_best_segments(transcriptions, mode="RELAXED")
    return [
        {"start": s["start"], "end": s["end"], "reason": s.get("reason", "")}
        for s in raw[:max_seg * 2]
        if min_dur <= (s["end"] - s["start"]) <= max_dur
    ][:max_seg]
