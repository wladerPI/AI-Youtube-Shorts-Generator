def decide_camera_events(transcript_text, vw, target_w, duration):
    events = []
    text = transcript_text.lower()

    if "olha" in text or "repara" in text:
        events.append({
            "start": duration * 0.15,
            "end": duration * 0.35,
            "target_x": int(vw * 0.65)
        })

    if "aqui" in text or "nesse ponto" in text:
        events.append({
            "start": duration * 0.5,
            "end": duration * 0.7,
            "target_x": int(vw * 0.35)
        })

    return events
