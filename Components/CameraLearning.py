# Components/CameraLearning.py

import json
import os
from statistics import mean

DATA_PATH = "learning/camera_learning.json"


def load_learning_data():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_learning_data(data):
    os.makedirs("learning", exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def register_video_result(
    viral_score: int,
    attention_score: int,
    camera_events: list,
    duration: float
):
    data = load_learning_data()

    data.append({
        "viral_score": viral_score,
        "attention_score": attention_score,
        "duration": duration,
        "camera_events": camera_events
    })

    save_learning_data(data)


def analyze_best_patterns(min_samples=5):
    data = load_learning_data()

    if len(data) < min_samples:
        return {}

    grouped = {}

    for d in data:
        for ev in d["camera_events"]:
            key = ev["camera"]
            grouped.setdefault(key, []).append(d["attention_score"])

    patterns = {
        k: mean(v)
        for k, v in grouped.items()
        if len(v) >= min_samples
    }

    return patterns
