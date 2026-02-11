# Components/SegmentMemory.py

import json
import os

MEMORY_PATH = "learning/segment_memory.json"


def remember_segment(segment):
    os.makedirs("learning", exist_ok=True)

    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(segment)

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
