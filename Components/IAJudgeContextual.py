# Components/IAJudgeContextual.py

def judge_with_context(summary):
    """
    Julgamento inteligente para LIVES LONGAS
    """

    viral = summary["viral_score"]
    retention = summary["retention_score"]
    drop = summary["drop_risk"]
    stability = summary["stability"]
    duration = summary["duration"]

    decision = "DESCARTADO"
    confidence = 70
    explanation = ""

    # ✅ APROVADO
    if retention >= 60 and viral >= 45:
        decision = "APROVADO"
        confidence = 90
        explanation = "Alta retenção e bom potencial viral para shorts de live."

    # 🔄 RERENDER
    elif retention >= 45 and viral >= 30:
        decision = "RERENDER"
        confidence = 75
        explanation = (
            "Conteúdo bom, mas pode performar melhor com "
            "câmera mais agressiva ou timing ajustado."
        )

    else:
        explanation = (
            "Baixa retenção ou risco elevado de queda "
            "para conteúdo de live longa."
        )

    return {
        "decision": decision,
        "confidence": confidence,
        "explanation": explanation
    }
