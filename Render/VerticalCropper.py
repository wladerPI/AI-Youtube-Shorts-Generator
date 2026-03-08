# Render/VerticalCropper.py - VERSÃO COM ÁUDIO CORRIGIDA
"""
=============================================================================
VERTICAL CROPPER COM ÁUDIO - VERSÃO FINAL
=============================================================================

CORREÇÃO CRÍTICA:
- cv2.VideoWriter NÃO suporta áudio!
- Solução: Renderizar vídeo com OpenCV, depois adicionar áudio com ffmpeg

=============================================================================
"""

import cv2
import numpy as np
import subprocess
import os
from pathlib import Path


def render_vertical_video(video_in, video_out, meme_events=None, session_id=None):
    """
    Renderiza vídeo vertical PRESERVANDO ÁUDIO.
    
    FUNCIONAMENTO:
    1. Renderiza vídeo vertical com OpenCV (sem áudio)
    2. Adiciona áudio do vídeo original com ffmpeg
    """
    print(f"🎬 Renderizando: {Path(video_in).name} → {Path(video_out).name}")
    
    # Arquivo temporário SEM áudio
    temp_video = str(Path(video_out).with_suffix('')) + "_temp.mp4"
    
    # Abrir vídeo
    cap = cv2.VideoCapture(video_in)
    
    if not cap.isOpened():
        print(f"❌ Erro ao abrir vídeo: {video_in}")
        return False
    
    # Propriedades do vídeo
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Dimensões do output (vertical)
    output_width = 1080
    output_height = 1920
    
    print(f"   Input: {width}x{height} @ {fps:.1f} FPS")
    print(f"   Output: {output_width}x{output_height}")
    
    # Criar writer (SEM áudio)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, fps, (output_width, output_height))
    
    if not out.isOpened():
        print(f"❌ Erro ao criar writer")
        cap.release()
        return False
    
    # Processar frames
    frame_num = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Progresso
        if frame_num % (int(fps) * 10) == 0:
            progress = (frame_num / total_frames) * 100
            print(f"      [{progress:5.1f}%] Frame {frame_num}/{total_frames}")
        
        # Comportamento: centro fixo
        half_width = output_width // 2
        center_x = width // 2
        x1 = max(0, center_x - half_width)
        x2 = min(width, center_x + half_width)
        y1 = 0
        y2 = height
        
        # Crop e resize
        cropped = frame[y1:y2, x1:x2]
        
        # Garantir dimensões corretas
        if cropped.shape[1] != output_width or cropped.shape[0] != height:
            cropped = cv2.resize(cropped, (output_width, height))
        
        # Resize para vertical
        vertical = cv2.resize(cropped, (output_width, output_height))
        
        # Escrever frame
        out.write(vertical)
        
        frame_num += 1
    
    # Liberar recursos
    cap.release()
    out.release()
    
    print(f"   ✅ Vídeo renderizado (sem áudio)")
    
    # ADICIONAR ÁUDIO COM FFMPEG
    print(f"   🎵 Adicionando áudio...")
    
    cmd = [
        'ffmpeg',
        '-i', temp_video,      # Vídeo sem áudio
        '-i', video_in,        # Vídeo original (com áudio)
        '-map', '0:v:0',       # Vídeo do primeiro input
        '-map', '1:a:0',       # Áudio do segundo input
        '-c:v', 'copy',        # Copiar vídeo (não re-encode)
        '-c:a', 'aac',         # Encode áudio para aac
        '-b:a', '192k',        # Bitrate
        '-shortest',           # Terminar quando o menor acabar
        '-y',
        video_out
    ]
    
    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Limpar temp
    if os.path.exists(temp_video):
        os.remove(temp_video)
    
    if result.returncode == 0:
        print(f"   ✅ Renderização completa COM ÁUDIO!")
        return True
    else:
        print(f"   ❌ Erro ao adicionar áudio: {result.stderr[:200]}")
        return False


# =============================================================================
# TESTE
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python VerticalCropper.py <input.mp4> <output.mp4>")
        sys.exit(1)
    
    video_in = sys.argv[1]
    video_out = sys.argv[2]
    
    success = render_vertical_video(video_in, video_out)
    
    if success:
        print("✅ Sucesso!")
    else:
        print("❌ Falhou!")
        sys.exit(1)
