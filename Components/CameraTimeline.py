# Components/CameraTimeline.py

class CameraTimeline:
    def __init__(self):
        self.events = []

    def add_event(self, start, end, target_x):
        self.events.append({
            "start": start,
            "end": end,
            "target_x": target_x
        })

    def get_x(self, t, default_x):
        for e in self.events:
            if e["start"] <= t <= e["end"]:
                return e["target_x"]
        return default_x
