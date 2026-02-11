# Components/AttentionCurve.py
"""
=============================================================================
CURVA DE ATENÇÃO BASEADA EM ÁUDIO
=============================================================================

O QUE FAZ:
  Usa RMS (Root Mean Square) do áudio para gerar uma curva de "energia"
  ao longo do tempo. Valores normalizados 0-1. Indica onde há picos
  de volume (risadas, gritos) vs silêncio.

POR QUE:
  Usado pelo RetentionScore para avaliar se o short mantém atenção.
  Curva com picos = mais dinâmico = melhor retenção.

ALTERAÇÕES:
  - Nenhuma alteração estrutural

O QUE AINDA PODE SER FEITO:
  - Detectar frequência de risada (200-800Hz) especificamente
  - Combinar com análise visual
=============================================================================
"""

import numpy as np
import librosa


def build_attention_curve(
    audio_path: str,
    duration: float,
    fps: int = 10
):
    """
    Retorna lista de valores 0-1 representando a "atenção" ao longo do tempo.
    Interpola para ter expected_len = duration * fps pontos.
    """
    y, sr = librosa.load(audio_path, sr=None)
    hop_length = int(sr / fps)

    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

    if len(rms) == 0:
        return [0.0]

    rms_norm = (rms - rms.min()) / (rms.max() - rms.min() + 1e-6)

    expected_len = int(duration * fps)
    curve = np.interp(
        np.linspace(0, len(rms_norm), expected_len),
        np.arange(len(rms_norm)),
        rms_norm
    )

    return curve.tolist()
