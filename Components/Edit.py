# Components/Edit.py
"""
=============================================================================
EDIÇÃO DE VÍDEO — EXTRAÇÃO DE ÁUDIO E CORTE
=============================================================================

O QUE FAZ:
  - extractAudio: extrai áudio do vídeo em WAV (para transcrição)
  - crop_video: corta um trecho (start→end) do vídeo
  - smart_vertical_crop: crop vertical com decisão editorial (meme/reaction)

POR QUE USA MOVIEPY:
  Preserva áudio corretamente. OpenCV (cv2) não lida com áudio.

ALTERAÇÕES:
  - Nenhuma alteração estrutural; usado como estava
  - smart_vertical_crop existe mas NÃO é usado no pipeline atual
  - O pipeline usa Render/VerticalCropper.py (com MoviePy) para o vertical

O QUE AINDA PODE SER FEITO:
  - Usar FFmpeg diretamente para cortes mais rápidos
  - Remover prints de debug excessivos
  - Integrar smart_vertical_crop como alternativa ao VerticalCropper
=============================================================================
"""

from moviepy.editor import (
    VideoFileClip,
    CompositeVideoClip,
    vfx
)
import os
import inspect
import numpy as np

# =========================================================
# ETAPA A — EXTRAÇÃO DE ÁUDIO
# =========================================================

def extractAudio(video_path, output_audio_path):
    """
    Extrai a faixa de áudio do vídeo e salva em WAV.
    Usado antes da transcrição com Whisper.
    """
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(output_audio_path)
    clip.close()
    print(f"✅ Áudio extraído: {output_audio_path}")


# =========================================================
# ETAPA B — CORTE DE VÍDEO
# =========================================================

def crop_video(input_video_path, output_video_path, start, end):
    """
    Corta o vídeo do segundo 'start' até 'end'.
    Preserva áudio. Saída em MP4 (H.264 + AAC).
    """
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"❌ Vídeo não encontrado: {input_video_path}")

    if start >= end:
        raise ValueError("❌ start não pode ser maior ou igual a end")

    clip = VideoFileClip(input_video_path)
    video_duration = int(clip.duration)

    if start >= video_duration:
        raise ValueError("❌ start maior que duração do vídeo")

    end = min(end, video_duration)

    subclip = clip.subclip(start, end)
    subclip.write_videofile(
        output_video_path,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4
    )

    clip.close()
    subclip.close()
    print("✅ Corte finalizado com sucesso")


# =========================================================
# ETAPA K — CÂMERA INTELIGENTE (alternativa)
# =========================================================
# NOTA: Esta função existe mas NÃO é usada no pipeline atual.
# O pipeline usa Render/VerticalCropper.py com MemeCornerDetector.

def smart_vertical_crop(
    input_clip: VideoFileClip,
    highlight_reason: str,
    output_path: str,
    target_size=(1080, 1920)
):
    """
    Crop vertical com decisão editorial baseada no motivo do highlight.
    Se reason contém "meme", "reação", "rage" → move para esquerda ou direita.
    Caso contrário → mantém centro.
    Movimento único e suave, sempre retorna ao centro.
    """
    W, H = input_clip.w, input_clip.h
    target_w, target_h = target_size

    CAMERA_CENTER = "CENTER"
    CAMERA_LEFT = "LEFT"
    CAMERA_RIGHT = "RIGHT"

    reason = highlight_reason.lower()

    # Decisão: meme/reaction → pan lateral | outro → centro
    if any(k in reason for k in ["meme", "reação", "rage", "timing"]):
        camera_state = np.random.choice([CAMERA_LEFT, CAMERA_RIGHT])
    else:
        camera_state = CAMERA_CENTER

    crop_w = int(H * (9 / 16))
    center_x = W // 2
    left_x = int(W * 0.25)
    right_x = int(W * 0.75)

    def get_x(state):
        if state == CAMERA_LEFT:
            return max(left_x - crop_w // 2, 0)
        elif state == CAMERA_RIGHT:
            return min(right_x - crop_w // 2, W - crop_w)
        return max(center_x - crop_w // 2, 0)

    x_start = get_x(CAMERA_CENTER)
    x_target = get_x(camera_state)

    duration = input_clip.duration
    move_duration = min(2.2, duration / 2)

    def crop_x(t):
        if camera_state == CAMERA_CENTER:
            return x_start
        if t < move_duration:
            alpha = t / move_duration
            return int(x_start + (x_target - x_start) * alpha)
        elif t < duration - move_duration:
            return x_target
        else:
            alpha = (t - (duration - move_duration)) / move_duration
            return int(x_target + (x_start - x_target) * alpha)

    cropped = input_clip.crop(
        x1=lambda t: crop_x(t),
        y1=0,
        x2=lambda t: crop_x(t) + crop_w,
        y2=H
    )

    vertical = cropped.resize(height=target_h)
    vertical.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4
    )

    input_clip.close()
    vertical.close()
    print(f"✅ Vertical inteligente gerado: {output_path}")
