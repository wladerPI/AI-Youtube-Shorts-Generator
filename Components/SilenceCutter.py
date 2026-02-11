from moviepy.editor import VideoFileClip, concatenate_videoclips
import numpy as np


def remove_silence_intelligently(
    input_video,
    output_video,
    silence_threshold=0.02,
    min_silence_duration=0.8,
    padding=0.15,
    analysis_fps=20
):
    clip = VideoFileClip(input_video)

    if clip.audio is None:
        clip.write_videofile(
            output_video,
            codec="libx264",
            audio_codec="aac"
        )
        clip.close()
        return

    duration = clip.duration
    step = 1.0 / analysis_fps

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
                if silence_duration >= min_silence_duration:
                    end_time = max(silence_start - padding, last_sound)
                    if end_time > last_sound:
                        segments.append((last_sound, end_time))
                    last_sound = current_time
                silence_start = None

    if last_sound < duration:
        segments.append((last_sound, duration))

    clips = [clip.subclip(s, e) for s, e in segments if e > s]

    if not clips:
        clip.write_videofile(
            output_video,
            codec="libx264",
            audio_codec="aac"
        )
        clip.close()
        return

    final = concatenate_videoclips(clips, method="compose")

    final.write_videofile(
        output_video,
        codec="libx264",
        audio_codec="aac"
    )

    clip.close()
    final.close()
