import numpy as np
from moviepy.editor import AudioFileClip

def detect_audio_peak(video_path: str, threshold: float = 0.6):
    try:
        audio = AudioFileClip(video_path)
        samples = audio.to_soundarray(fps=22050)
        volume = np.linalg.norm(samples, axis=1)

        peak_index = np.argmax(volume)
        peak_value = volume[peak_index]

        if peak_value < threshold:
            return None

        peak_time = peak_index / 22050
        audio.close()
        return peak_time

    except Exception as e:
        print(f"[AUDIO ERROR] {e}")
        return None
