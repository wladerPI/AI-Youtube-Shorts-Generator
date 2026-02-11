# Components/VisualTracker.py

import cv2
import numpy as np
from Config import VIDEO_WIDTH, VERTICAL_WIDTH

def detect_active_x(frame):
    """
    Retorna o X ideal onde a janela vertical deve focar
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)

    thresh = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)[1]
    motion = np.sum(thresh, axis=0)

    center_x = int(np.argmax(motion))
    half = VERTICAL_WIDTH // 2

    left = max(0, center_x - half)
    right = min(VIDEO_WIDTH - VERTICAL_WIDTH, left)

    return left
