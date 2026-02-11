# Components/HookDetector.py

def detect_hook_strength(transcriptions, clip_start, clip_end):
    """
    Analisa os primeiros segundos do corte
    para detectar força de hook inicial
    """

    hook_text = []
    hook_duration = 3.0

    for text, start, end in transcriptions:
        if start >= clip_start and start <= clip_start + hook_duration:
            hook_text.append(text.lower())

    full = " ".join(hook_text)

    score = 0

    if any(w in full for w in ["olha", "mano", "presta", "atenção", "cara"]):
        score += 30
    if "!" in full or "?" in full:
        score += 20
    if len(full.split()) >= 6:
        score += 20

    if score > 60:
        return "FORTE", score
    elif score > 35:
        return "MÉDIO", score
    else:
        return "FRACO", score
