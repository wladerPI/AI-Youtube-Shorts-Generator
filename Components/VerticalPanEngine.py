# Components/VerticalPanEngine.py

from Config import PAN_SMOOTHING

def smooth_pan(current_x, target_x):
    return int(current_x + (target_x - current_x) * PAN_SMOOTHING)


def generate_pan_positions(frames, tracker):
    """
    Retorna lista de X para cada frame
    """
    pan_positions = []
    current_x = 0

    for frame in frames:
        target_x = tracker(frame)
        current_x = smooth_pan(current_x, target_x)
        pan_positions.append(current_x)

    return pan_positions

