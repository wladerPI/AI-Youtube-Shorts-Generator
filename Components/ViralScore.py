# Components/ViralScore.py
"""
=============================================================================
CÁLCULO DO SCORE VIRAL
=============================================================================

O QUE FAZ:
  Atribui pontuação 0-100 a um segmento com base em:
  - Duração (7-15s ideal para shorts)
  - Palavras-chave no reason: rage, grito, humor, meme, reação
  - Posição na live (início tem mais chance de hook)

POR QUE:
  Usado no ranking.json para ordenar shorts por potencial viral.
  Canal de Games/Humor: rage e memes têm prioridade.

ALTERAÇÕES:
  - Nenhuma alteração estrutural

O QUE AINDA PODE SER FEITO:
  - Incluir "rizada" como keyword de alta pontuação
  - Aprender com shorts que viralizaram (feedback)
=============================================================================
"""

def calculate_viral_score(start, end, reason):
    """
    Retorna score 0-100. reason vem do LLM ou do AISegmentSelector.
    """
    score = 0
    duration = end - start
    reason = (reason or "").lower()

    # Duração ideal para shorts
    if 7 <= duration <= 15:
        score += 30
    elif 16 <= duration <= 30:
        score += 20
    else:
        score += 10

    # Keywords de viralidade (canal Games/Humor)
    if "rage" in reason or "xing" in reason:
        score += 30
    if "grito" in reason:
        score += 25
    if "humor" in reason:
        score += 20
    if "meme" in reason:
        score += 18
    if "reação" in reason:
        score += 15

    # Início da live = mais engajamento
    if start <= 2:
        score += 25
    elif start <= 4:
        score += 15
    elif start <= 6:
        score += 5

    # Penalidades
    if duration > 40:
        score -= 15
    if start > 6:
        score -= 10

    return max(0, min(100, score))
