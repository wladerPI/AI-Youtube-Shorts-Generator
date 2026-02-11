# Components/RetentionScore.py
"""
=============================================================================
MÉTRICAS DE RETENÇÃO
=============================================================================

O QUE FAZ:
  Analisa a curva de atenção (de AttentionCurve) e calcula:
  - score: 0-100 (média da curva + estabilidade)
  - drop_risk: baixo/medio/alto (quedas bruscas = risco de saída)
  - stability: penaliza quedas > 30% entre pontos consecutivos

POR QUE:
  Shorts com retenção alta = espectador assiste até o fim.
  Algoritmo do YouTube/TikTok favorece retenção.

ALTERAÇÕES:
  - Nenhuma alteração estrutural

O QUE AINDA PODE SER FEITO:
  - Normalizar drop_risk para SmartRanking em português (baixo/medio/alto)
=============================================================================
"""

def calculate_retention_metrics(curve: list):
    """
    curve: lista de valores 0-1 da AttentionCurve.
    Retorna dict com score, drop_risk, stability.
    """
    if not curve:
        return {
            "score": 0,
            "drop_risk": "alto",
            "stability": 0
        }

    avg = sum(curve) / len(curve)

    # Conta quedas bruscas (> 30% entre pontos)
    drops = sum(
        1 for i in range(1, len(curve))
        if curve[i] < curve[i - 1] * 0.7
    )

    stability = max(0, 100 - drops * 5)
    score = int((avg * 70) + (stability * 0.3))

    if score > 75:
        risk = "baixo"
    elif score > 50:
        risk = "medio"
    else:
        risk = "alto"

    return {
        "score": score,
        "drop_risk": risk,
        "stability": stability
    }
