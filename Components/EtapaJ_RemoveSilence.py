# Components/EtapaJ_RemoveSilence.py
"""
=============================================================================
REMOÇÃO DE SILÊNCIOS LONGOS
=============================================================================

O QUE FAZ:
  Analisa o áudio frame a frame, detecta trechos silenciosos (volume baixo)
  e os remove. Concatena apenas os trechos com som. Reduz a duração do short
  eliminando pausas longas.

PARÂMETROS:
  - silence_threshold: volume abaixo disso = silêncio
  - min_silence: só remove silêncios com >= 0.8s
  - padding: mantém 0.15s antes/depois para não cortar início de fala

POR QUE É IMPORTANTE:
  Lives têm muitas pausas. Shorts precisam ser dinâmicos. Cortar silêncios
  mantém o ritmo e reduz duração sem perder conteúdo.

ALTERAÇÕES:
  - Nenhuma alteração estrutural

O QUE AINDA PODE SER FEITO:
  - Usar VAD (Voice Activity Detection) mais sofisticado
  - Preservar pequenas pausas dramáticas
  - Threshold adaptativo por trecho
=============================================================================
"""

from moviepy.editor import VideoFileClip, concatenate_videoclips
import numpy as np


def remove_silence(
    video_in,
    video_out,
    silence_threshold=0.02,
    min_silence=0.8,
    padding=0.15,
    analysis_fps=20
):
    """
    Remove silêncios >= min_silence segundos. Concatena os trechos sonoros.
    Se vídeo não tem áudio, apenas copia.
    """
    clip = VideoFileClip(video_in)

    if clip.audio is None:
        clip.write_videofile(
            video_out,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4
        )
        clip.close()
        return

    duration = clip.duration
    step = 1.0 / analysis_fps

    # Amostra volumes ao longo do vídeo
    times = np.arange(0, duration, step)
    volumes = []
    for t in times:
        try:
            frame = clip.audio.get_frame(t)
            volume = np.linalg.norm(frame) if frame is not None else 0.0
        except Exception:
            volume = 0.0
        volumes.append(volume)

    silent = np.array(volumes) < silence_threshold

    # Encontra segmentos sonoros (entre silêncios longos)
    segments = []
    last_sound = 0.0
    silence_start = None

    for i, is_silent in enumerate(silent):
        current_time = times[i]

        if is_silent:
            if silence_start is None:
                silence_start = current_time
        else:
            if silence_start is not None:
                silence_duration = current_time - silence_start
                if silence_duration >= min_silence:
                    end_time = max(silence_start - padding, last_sound)
                    if end_time > last_sound:
                        segments.append((last_sound, end_time))
                    last_sound = current_time
                silence_start = None

    if last_sound < duration:
        segments.append((last_sound, duration))

    final_clips = [clip.subclip(s, e) for s, e in segments if e > s]

    if not final_clips:
        raise RuntimeError("❌ Nenhum trecho sonoro encontrado")

    final = concatenate_videoclips(final_clips, method="compose")

    final.write_videofile(
        video_out,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4
    )

    clip.close()
    final.close()
