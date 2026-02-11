# Components/SmartRanking.py
"""
=============================================================================
SCORE FINAL DE RANKING
=============================================================================

O QUE FAZ:
  Combina viral_score, retention_score, duration e drop_risk em um
  score único 0-100 para ordenar os shorts no ranking.json.

PESOS:
  - Retention: 60% (mais importante)
  - Duração ideal 7-30s: +20
  - Drop risk alto: penalidade

POR QUE:
  Ordenar shorts por qualidade antes da publicação.
  O usuário pode priorizar os de maior rank.

ALTERAÇÕES:
  - Aceita drop_risk em português (baixo/medio/alto) e inglês (LOW/MEDIUM/HIGH)

O QUE AINDA PODE SER FEITO:
  - Peso configurável
  - Incluir viral_score no cálculo
=============================================================================
"""

def calculate_rank_score(summary: dict) -> float:
    """
    summary deve ter: retention_score, duration, drop_risk (opcional)
    """
    score = 0.0

    retention = summary.get("retention_score", 0)
    try:
        retention = float(retention)
    except (TypeError, ValueError):
        retention = 0.0
    score += retention * 0.6

    duration = summary.get("duration", 0)
    try:
        duration = float(duration)
    except (TypeError, ValueError):
        duration = 0.0
    if 7 <= duration <= 30:
        score += 20
    else:
        score -= 10

    drop_risk = summary.get("drop_risk", 0)
    if isinstance(drop_risk, str):
        drop_risk = drop_risk.upper()
        if drop_risk in ("LOW", "BAIXO"):
            drop_risk = 10
        elif drop_risk in ("MEDIUM", "MEDIO"):
            drop_risk = 30
        elif drop_risk in ("HIGH", "ALTO"):
            drop_risk = 60
        else:
            drop_risk = 0
    elif isinstance(drop_risk, (list, tuple)):
        drop_risk = 30

    try:
        drop_risk = float(drop_risk)
    except (TypeError, ValueError):
        drop_risk = 0.0

    score -= drop_risk * 0.3

    score = max(0, min(100, score))
    return round(score, 2)
