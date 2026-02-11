# Components/MemeCornerDetector.py
"""
=============================================================================
DETECÇÃO DE MEMES/FACES NOS CANTOS DA TELA
=============================================================================

O QUE FAZ:
  Analisa o vídeo e detecta quando há faces ou atividade visual nos cantos
  esquerdo e direito. Retorna eventos [{"start", "end", "region": "left"|"right"}].
  Usado pelo VerticalCropper para fazer pan da câmera e mostrar o meme.

POR QUE:
  O canal usa memes que aparecem nos cantos. A câmera deve pan para lá,
  mostrar por alguns segundos e retornar ao centro.

MÉTODO:
  1. Usa haarcascade (OpenCV) para detectar faces nas regiões 0-25% e 75-100%
  2. Se haarcascade não existir: fallback por diferença de movimento entre
     terço esquerdo e direito do frame

ALTERAÇÕES:
  - Componente criado do zero para esta funcionalidade

O QUE AINDA PODE SER FEITO:
  - Detecção de objetos (YOLO) além de faces para memes não-humanos
  - Ajuste fino do min_face_size por resolução
  - Detectar "overlays" (imagens sobrepostas) nos cantos
=============================================================================
"""

import cv2
import os
import numpy as np


def detect_meme_corners(
    video_path: str,
    sample_interval: float = 0.5,
    show_duration: float = 2.5,
    face_region_ratio: float = 0.25,
    min_face_size: int = 40
) -> list:
    """
    Retorna lista de eventos: [{"start": t, "end": t+duration, "region": "left"|"right"}, ...]
    show_duration: quanto tempo manter o pan no meme (segundos)
    """
    cascade_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "haarcascade_frontalface_default.xml"
    )

    if not os.path.exists(cascade_path):
        return _detect_by_motion_regions(video_path, sample_interval, show_duration)

    face_cascade = cv2.CascadeClassifier(cascade_path)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if frame_count > 0 else 0

    if duration <= 0:
        cap.release()
        return []

    events = []
    sample_every = max(1, int(fps * sample_interval))
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_every != 0:
            frame_idx += 1
            continue

        t = frame_idx / fps
        h, w = frame.shape[:2]

        # Regiões: esquerda 0-25%, direita 75-100%
        left_x1, left_x2 = 0, int(w * face_region_ratio)
        right_x1, right_x2 = int(w * (1 - face_region_ratio)), w

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        left_gray = gray[:, left_x1:left_x2]
        right_gray = gray[:, right_x1:right_x2]

        left_faces = face_cascade.detectMultiScale(
            left_gray, 1.1, 5, minSize=(min_face_size, min_face_size)
        )
        right_faces = face_cascade.detectMultiScale(
            right_gray, 1.1, 5, minSize=(min_face_size, min_face_size)
        )

        if len(left_faces) > 0:
            events.append({
                "start": max(0, t - 0.2),
                "end": min(duration, t + show_duration),
                "region": "left"
            })
        if len(right_faces) > 0:
            events.append({
                "start": max(0, t - 0.2),
                "end": min(duration, t + show_duration),
                "region": "right"
            })

        frame_idx += 1

    cap.release()
    events = _merge_overlapping_events(events)
    return events


def _detect_by_motion_regions(video_path, sample_interval, show_duration):
    """
    Fallback: quando não há haarcascade. Detecta movimento forte em um
    terço da tela (esquerda ou direita) comparado ao outro.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    sample_every = max(1, int(fps * sample_interval))
    prev_left = None
    prev_right = None
    events = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_every == 0:
            t = frame_idx / fps
            h, w = frame.shape[:2]
            left_roi = frame[:, :w//3]
            right_roi = frame[:, 2*w//3:]

            left_gray = cv2.cvtColor(left_roi, cv2.COLOR_BGR2GRAY)
            right_gray = cv2.cvtColor(right_roi, cv2.COLOR_BGR2GRAY)

            if prev_left is not None:
                left_diff = cv2.absdiff(left_gray, prev_left)
                right_diff = cv2.absdiff(right_gray, prev_right)
                left_int = left_diff.mean()
                right_int = right_diff.mean()

                threshold = 25
                if left_int > threshold and left_int > right_int * 1.3:
                    events.append({"start": max(0, t - 0.2), "end": t + show_duration, "region": "left"})
                elif right_int > threshold and right_int > left_int * 1.3:
                    events.append({"start": max(0, t - 0.2), "end": t + show_duration, "region": "right"})

            prev_left = left_gray
            prev_right = right_gray

        frame_idx += 1

    cap.release()
    return _merge_overlapping_events(events)


def _merge_overlapping_events(events):
    """Junta eventos do mesmo lado que se sobrepõem ou estão próximos."""
    if not events:
        return []

    events = sorted(events, key=lambda e: e["start"])
    merged = [events[0].copy()]

    for e in events[1:]:
        last = merged[-1]
        if e["region"] == last["region"] and e["start"] <= last["end"] + 1:
            last["end"] = max(last["end"], e["end"])
        elif e["start"] > last["end"] + 0.5:
            merged.append(e.copy())

    return merged
