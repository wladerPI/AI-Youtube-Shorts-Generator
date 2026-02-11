# Components/SegmentScorer.py

import re


POWER_WORDS = [
    "mano", "caralho", "absurdo", "insano", "bizarro",
    "ninguém", "todo mundo", "olha isso", "presta atenção",
    "isso muda tudo", "ninguém fala", "ninguém percebe"
]


def score_segment(text: str):
    text_l = text.lower()
    score = 0
    reasons = []

    for w in POWER_WORDS:
        if w in text_l:
            score += 12
            reasons.append(f"palavra forte: {w}")

    if "?" in text:
        score += 10
        reasons.append("pergunta direta")

    if re.search(r"\d+", text):
        score += 8
        reasons.append("números concretos")

    if len(text.split()) < 25:
        score += 10
        reasons.append("frase curta e direta")

    if score > 100:
        score = 100

    reason_text = ", ".join(reasons) if reasons else "fala relevante"

    return score, reason_text
