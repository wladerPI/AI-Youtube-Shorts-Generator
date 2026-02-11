# Render/VerticalCropper.py
"""
=============================================================================
RENDERIZAÇÃO VERTICAL 9:16 COM ÁUDIO
=============================================================================

O QUE FAZ:
  Converte vídeo horizontal em vertical 9:16 (Shorts/TikTok/Reels).
  USA MOVIEPY (não OpenCV) para PRESERVAR O ÁUDIO.
  Se pan_engine=True, detecta memes nos cantos e faz pan da câmera.

ALTERAÇÃO CRÍTICA:
  O código original usava cv2.VideoWriter, que NÃO suporta áudio.
  Os shorts saíam SEM SOM. Foi reescrito com MoviePy.

FLUXO DO PAN:
  - Por padrão: crop central (centro da tela)
  - Quando MemeCornerDetector encontra face/atividade no canto: pan suave
    para esquerda ou direita, mantém 2s, retorna ao centro com transição 0.3s

O QUE AINDA PODE SER FEITO:
  - Easing mais sofisticado
  - Configurar show_duration por tipo de evento
  - Suportar zoom opcional em momentos-chave
=============================================================================
"""

import os
from moviepy.editor import VideoFileClip

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Components.MemeCornerDetector import detect_meme_corners


def _get_pan_x(t, vw, crop_w, pan_events):
    """
    Posição X do crop no tempo t.
    Centro por padrão. Durante eventos: left_x (0) ou right_x (vw - crop_w).
    Transição suave (smoothstep) de 0.3s na entrada e saída do evento.
    """
    center_x = (vw - crop_w) // 2
    left_x = 0
    right_x = vw - crop_w

    for ev in pan_events:
        start, end = ev["start"], ev["end"]
        region = ev.get("region", "center")
        trans = 0.3

        if region == "left":
            target = left_x
        elif region == "right":
            target = right_x
        else:
            continue

        if t < start or t > end:
            continue

        # Entrada: centro → target
        if t < start + trans:
            alpha = (t - start) / trans
            alpha = alpha * alpha * (3 - 2 * alpha)  # smoothstep
            return int(center_x + (target - center_x) * alpha)
        # Saída: target → centro
        if t > end - trans:
            alpha = (end - t) / trans
            alpha = alpha * alpha * (3 - 2 * alpha)
            return int(target + (center_x - target) * (1 - alpha))

        return target

    return center_x


def render_vertical_video(
    input_video,
    output_video,
    pan_engine=True,
    target_width=1080,
    target_height=1920
):
    """
    Renderiza vídeo vertical. SEMPRE preserva áudio.
    pan_engine=True: chama MemeCornerDetector e aplica pan nos eventos.
    """
    clip = VideoFileClip(input_video)
    vw, vh = clip.size
    duration = clip.duration

    # Largura do crop para proporção 9:16
    crop_w = int(vh * 9 / 16)
    if crop_w > vw:
        crop_w = vw

    pan_events = []
    if pan_engine:
        try:
            pan_events = detect_meme_corners(
                input_video,
                sample_interval=0.4,
                show_duration=2.0
            )
            if pan_events:
                print(f"   🎯 {len(pan_events)} eventos de meme detectados nos cantos")
        except Exception as e:
            print(f"   ⚠️ MemeCornerDetector: {e} — usando centro fixo")

    def crop_frame(get_frame, t):
        frame = get_frame(t)
        x = _get_pan_x(t, vw, crop_w, pan_events)
        x = max(0, min(x, vw - crop_w))
        return frame[0:vh, x:x + crop_w]

    vertical = clip.fl(crop_frame)

    # CRUCIAL: preservar áudio
    if clip.audio:
        vertical = vertical.set_audio(clip.audio)

    vertical = vertical.resize(height=target_height)

    vertical.write_videofile(
        output_video,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4
    )

    clip.close()
    vertical.close()

    print(f"✅ Vertical render finalizado (com áudio): {output_video}")
    return output_video
