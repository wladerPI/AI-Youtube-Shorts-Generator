# Components/VisualEvents.py

import cv2

def detect_visual_activity(video_path, threshold=30):
    """
    Detecta atividade visual (movimento forte),
    útil para identificar memes, overlays, reações.
    Retorna lista de eventos com tempo e intensidade.
    """

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    prev_gray = None
    events = []
    frame_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            intensity = diff.mean()

            if intensity > threshold:
                t = frame_index / fps
                events.append({
                    "time": round(t, 3),
                    "intensity": float(intensity)
                })

        prev_gray = gray
        frame_index += 1

    cap.release()
    return events
