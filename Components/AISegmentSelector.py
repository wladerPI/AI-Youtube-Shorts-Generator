# Components/AISegmentSelector.py
"""
=============================================================================
SELETOR DE SEGMENTOS HEURÍSTICO (FALLBACK)
=============================================================================

O QUE FAZ:
  Seleção por regras fixas (sem LLM):
  - Agrupa palavras em janelas de 3 palavras
  - Pontua por densidade de palavras, keywords fortes, pontuação (!?)
  - Duração ideal 15-45s

USO:
  Chamado por SegmentSelectorLLM quando LLM falha ou OPENAI_API_KEY ausente.

POR QUE EXISTE:
  Garantir que o pipeline funcione mesmo sem API da OpenAI.

ALTERAÇÕES:
  - Nenhuma alteração estrutural

O QUE AINDA PODE SER FEITO:
  - Adicionar "hahaha", "kkk" como keywords de risada
  - Ajustar para durações 30s-3min quando usado como fallback do LLM
=============================================================================
"""

import re

KEYWORDS_STRONG = [
    "mano", "cara", "olha", "tipo", "basicamente",
    "não faz sentido", "presta atenção", "o problema é",
    "vou explicar", "acontece que", "na real",
    "caralho", "porra", "puta", "meu deus", "cacete"
]


def select_best_segments(transcriptions, mode="RELAXED"):
    """
    Retorna lista de segmentos com start, end, score, reason.
    mode RELAXED: critérios mais permissivos.
    """
    segments = []

    MIN_DURATION = 10 if mode == "RELAXED" else 15
    MAX_DURATION = 90 if mode == "RELAXED" else 60
    MIN_SCORE = 18 if mode == "RELAXED" else 28
    WINDOW_SIZE = 3 if mode == "RELAXED" else 2

    for i in range(len(transcriptions) - WINDOW_SIZE):
        texts = []
        start = transcriptions[i][1]
        end = transcriptions[i + WINDOW_SIZE][2]

        duration = end - start
        if duration < MIN_DURATION or duration > MAX_DURATION:
            continue

        for j in range(WINDOW_SIZE + 1):
            texts.append(transcriptions[i + j][0])

        full_text = " ".join(texts)
        words = full_text.split()
        word_density = len(words) / max(duration, 1)

        score = 0

        if word_density > 1.4:
            score += 10
        if word_density > 2.0:
            score += 10

        for kw in KEYWORDS_STRONG:
            if kw in full_text.lower():
                score += 8
                break

        score += full_text.count("!") * 2
        score += full_text.count("?") * 2

        if 15 <= duration <= 45:
            score += 15
        elif duration <= 60:
            score += 8

        segments.append({
            "start": start,
            "end": end,
            "score": score,
            "reason": full_text[:200]
        })

    good = [s for s in segments if s["score"] >= MIN_SCORE]

    # Fallback: se nenhum passou, pega trechos aleatórios
    if not good:
        for i in range(0, len(transcriptions) - 2, 5):
            start = transcriptions[i][1]
            end = transcriptions[i + 2][2]
            if end - start >= 12:
                good.append({
                    "start": start,
                    "end": end,
                    "score": 1,
                    "reason": transcriptions[i][0][:120]
                })
            if len(good) >= 6:
                break

    good.sort(key=lambda x: x["score"], reverse=True)
    max_clips = 8 if mode == "RELAXED" else 5

    return good[:max_clips]
