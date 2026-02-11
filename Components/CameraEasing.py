def ease_in_out(t: float) -> float:
    """
    Suavização profissional (0 → 1)
    """
    return t * t * (3 - 2 * t)
