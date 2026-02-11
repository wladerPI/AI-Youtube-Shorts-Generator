# Components/CameraMemory.py

_last_camera_state = None


def get_last_camera_state():
    """
    Retorna o último estado da câmera:
    CENTER, LEFT ou RIGHT
    """
    return _last_camera_state


def set_last_camera_state(state: str):
    global _last_camera_state
    if state in ("LEFT", "CENTER", "RIGHT"):
        _last_camera_state = state
