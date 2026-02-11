# Config.py
"""
=============================================================================
CONFIGURAÇÕES GLOBAIS DO PROJETO
=============================================================================

O QUE FAZ:
  Define constantes usadas em todo o pipeline: resolução de vídeo,
  dimensões verticais, suavização do pan, thresholds de áudio.

POR QUE EXISTE:
  Centralizar configurações evita "números mágicos" espalhados no código.
  Alterar resolução ou suavidade do pan em um único lugar.

ALTERAÇÕES:
  - Original: valores padrão para 1080p
  - Mantido para compatibilidade com FaceCrop, CameraLimits, etc.

O QUE AINDA PODE SER FEITO:
  - Ler de arquivo .env ou config.yaml para fácil ajuste
  - Auto-detectar resolução do vídeo de entrada
  - Configurações por modo (TEST/LIVE/INSANO)
=============================================================================
"""

# Resolução esperada do vídeo de entrada (1080p)
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Dimensões do crop vertical 9:16 (formato Shorts/TikTok/Reels)
# 608 é a largura do crop para manter proporção dentro de 1080p
VERTICAL_WIDTH = 608
VERTICAL_HEIGHT = 1080

# Suavização do movimento de pan (0.0 = instantâneo, 0.2 = mais suave)
# Quanto menor o valor, mais suave o movimento da câmera
PAN_SMOOTHING = 0.15

# Limiar para detectar picos de áudio (risadas, gritos)
# Valores acima disso são considerados "eventos de áudio"
AUDIO_PEAK_THRESHOLD = 0.65

# Duração mínima que o pan deve permanecer em uma posição (em segundos)
MIN_PAN_DURATION = 0.4
