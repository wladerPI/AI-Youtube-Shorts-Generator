# Components/CameraAIDirector.py

from Components.CameraLearning import analyze_best_patterns


def ai_decide_camera_bias(default_state="CENTER"):
    patterns = analyze_best_patterns()

    if not patterns:
        return default_state

    best = max(patterns.items(), key=lambda x: x[1])[0]
    return best


def apply_ai_bias_to_events(events, vw, target_w):
    bias = ai_decide_camera_bias()

    for ev in events:
        if bias == "LEFT":
            ev["target_x"] = int(vw * 0.15)
        elif bias == "RIGHT":
            ev["target_x"] = int(vw * 0.65)
        else:
            ev["target_x"] = int((vw - target_w) / 2)

    return events
