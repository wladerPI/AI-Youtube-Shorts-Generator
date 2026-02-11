# Components/CameraLimits.py

def apply_camera_limits(
    video_width: int,
    crop_width: int,
    positions: list,
    duration: float
) -> list:
    """
    Aplica limites profissionais:
    - Nunca atravessar tela inteira
    - Nunca mover rápido demais
    - Nunca exagerar
    """

    MAX_TRAVEL_RATIO = 0.35   # no máx 35% da largura total
    MIN_HOLD_TIME = 0.6       # pelo menos 600ms parado

    max_travel = int(video_width * MAX_TRAVEL_RATIO)
    center = (video_width - crop_width) // 2

    limited_positions = []

    for x in positions:
        delta = x - center

        if delta > max_travel:
            x = center + max_travel
        elif delta < -max_travel:
            x = center - max_travel

        limited_positions.append(x)

    # segurança extra: evita movimentos inúteis
    if len(set(limited_positions)) == 1:
        return [limited_positions[0]]

    return limited_positions
