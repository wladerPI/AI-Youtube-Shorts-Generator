def build_retention_curve(
    duration: float,
    audio_peak_time,
    camera_events: list,
    viral_score: int
):
    curve = []

    base_attention = min(0.4 + viral_score / 200, 0.85)

    curve.append({
        "time": 0.0,
        "attention": base_attention
    })

    if audio_peak_time:
        curve.append({
            "time": audio_peak_time,
            "attention": min(1.0, base_attention + 0.35)
        })

    for ev in camera_events:
        curve.append({
            "time": ev["time"],
            "attention": min(1.0, base_attention + 0.15)
        })

    if duration > 20:
        curve.append({
            "time": duration * 0.9,
            "attention": base_attention * 0.75
        })

    curve.sort(key=lambda x: x["time"])
    return curve
