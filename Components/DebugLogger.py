import json
import time

class DebugLogger:
    def __init__(self, output_path="debug_log.json"):
        self.output_path = output_path
        self.events = []

    def log(self, t, camera, audio_peak, intensity):
        self.events.append({
            "time": round(t, 2),
            "camera": camera,
            "audio_peak": audio_peak,
            "intensity": intensity
        })

    def save(self):
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.events, f, indent=2)
