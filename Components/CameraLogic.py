# Components/CameraLogic.py

def decide_camera_path(
    reason: str,
    transcript_text: str,
    viral_score: int = 0,
    audio_peak_time=None,
    previous_state: str = "CENTER"
) -> list:
    """
    Decide o caminho da câmera baseado em:
    - Viral Score
    - Pico de áudio
    - Contexto semântico
    - Estado anterior da câmera
    """

    reason = (reason or "").lower()
    text = (transcript_text or "").lower()
    previous_state = previous_state or "CENTER"

    # 🧠 SCORE MUITO BAIXO → câmera parada
    if viral_score < 40:
        return [previous_state]

    # 🔊 SCORE MÉDIO
    if 40 <= viral_score < 60:
        if audio_peak_time:
            return [previous_state, "LEFT", "CENTER"]
        return [previous_state]

    # 🔥 SCORE ALTO
    if viral_score >= 60:

        # Pico de áudio tem prioridade
        if audio_peak_time:
            return [previous_state, "RIGHT", "CENTER"]

        # Meme / reação
        if any(k in reason for k in [
            "meme", "risada", "reação", "engraçado", "grito"
        ]):
            return [previous_state, "LEFT", "CENTER"]

        # Pistas textuais
        if "direita" in text:
            return [previous_state, "RIGHT", "CENTER"]
        if "esquerda" in text:
            return [previous_state, "LEFT", "CENTER"]

        return [previous_state]

    return [previous_state]


def get_crop_x(video_width: int, crop_width: int, state: str) -> int:
    if state == "LEFT":
        return 0
    if state == "RIGHT":
        return video_width - crop_width
    return (video_width - crop_width) // 2
