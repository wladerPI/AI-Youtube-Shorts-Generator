# Components/CameraEventCollector.py

from Components.VisualEvents import detect_visual_activity
from Components.AudioEvents import detect_audio_peak

def collect_camera_events(
    video_path,
    vw,
    target_w
):
    """
    Junta eventos de áudio + vídeo
    e decide para onde a câmera deve ir.
    """

    events = []

    visual_events = detect_visual_activity(video_path)
    audio_peak = detect_audio_peak(video_path)

    # 🔊 Evento de áudio forte (risada / grito)
    if audio_peak:
        events.append({
            "start": max(audio_peak - 0.4, 0),
            "end": audio_peak + 0.8,
            "target_x": int((vw - target_w) * 0.5)
        })

    # 👀 Eventos visuais (memes aparecendo)
    for v in visual_events:
        pos = int((vw - target_w) * 0.75)
        if v["intensity"] > 45:
            pos = int((vw - target_w) * 0.1)

        events.append({
            "start": max(v["time"] - 0.2, 0),
            "end": v["time"] + 0.6,
            "target_x": pos
        })

    return events
