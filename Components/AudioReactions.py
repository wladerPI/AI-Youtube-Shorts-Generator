# Components/AudioReactions.py

import numpy as np

def detect_audio_peaks(audio_samples, threshold):
    peaks = []
    window = 2048

    for i in range(0, len(audio_samples), window):
        chunk = audio_samples[i:i+window]
        energy = np.sqrt(np.mean(chunk ** 2))

        if energy > threshold:
            peaks.append(i)

    return peaks
