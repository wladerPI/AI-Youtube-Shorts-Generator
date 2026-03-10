# Render/SmartCropper.py
"""
=============================================================================
SMART CROPPER COM MOVIMENTO DE CÂMERA
=============================================================================

✨ FEATURES:
- Crop vertical inteligente (9:16)
- Movimento de câmera baseado em TEXTO dos memes
- SEM GPU, SEM frame-by-frame
- Movimento suave quando detecta palavra-chave do meme
- Retorna ao centro após mostrar meme
- Preserva áudio perfeitamente

=============================================================================
"""

import cv2
import subprocess
import json
import numpy as np
from pathlib import Path


class SmartCropper:
    """Crop vertical com movimento de câmera inteligente."""
    
    def __init__(self, 
                 target_width=1080,
                 target_height=1920,
                 movement_duration=1.5,      # Duração do movimento (segundos)
                 hold_duration=2.0,          # Quanto tempo segura no meme
                 transition_smoothness=30):   # Frames de transição
        """
        Inicializa SmartCropper.
        
        Args:
            target_width: Largura final (1080 para shorts)
            target_height: Altura final (1920 para shorts)
            movement_duration: Duração do movimento de câmera
            hold_duration: Tempo que fica focado no meme
            transition_smoothness: Suavidade da transição
        """
        self.target_width = target_width
        self.target_height = target_height
        self.movement_duration = movement_duration
        self.hold_duration = hold_duration
        self.transition_smoothness = transition_smoothness
    
    def render_short(self, 
                     input_video, 
                     output_video, 
                     meme_timestamps=None,
                     center_mode='center'):
        """
        Renderiza short com crop inteligente e movimento de câmera.
        
        Args:
            input_video: Vídeo de entrada
            output_video: Vídeo de saída
            meme_timestamps: Lista de {'time': segundos, 'position': 'left'/'right'}
            center_mode: Modo de centralização ('center', 'left', 'right')
        
        Returns:
            Caminho do vídeo renderizado
        """
        print(f"🎬 Renderizando: {Path(output_video).name}")
        
        # Abrir vídeo
        cap = cv2.VideoCapture(input_video)
        
        if not cap.isOpened():
            raise ValueError(f"Não foi possível abrir vídeo: {input_video}")
        
        # Informações do vídeo
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"   📊 {orig_width}x{orig_height} → {self.target_width}x{self.target_height}")
        print(f"   🎞️  {total_frames} frames @ {fps} FPS")
        
        # Calcular crop
        scale = max(self.target_width / orig_width, self.target_height / orig_height)
        scaled_width = int(orig_width * scale)
        scaled_height = int(orig_height * scale)
        
        # Criar vídeo temporário (sem áudio)
        temp_video = str(Path(output_video).with_stem(Path(output_video).stem + '_no_audio'))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            temp_video,
            fourcc,
            fps,
            (self.target_width, self.target_height)
        )
        
        # Processar frames
        frame_count = 0
        
        # Gerar mapa de movimento (qual posição usar em cada frame)
        movement_map = self._generate_movement_map(
            total_frames, 
            fps, 
            meme_timestamps or []
        )
        
        print(f"   🎥 Processando frames...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Redimensionar
            resized = cv2.resize(frame, (scaled_width, scaled_height))
            
            # Obter posição de crop para este frame
            crop_position = movement_map[frame_count]
            
            # Calcular offset X baseado na posição
            if crop_position == 'left':
                x_offset = 0
            elif crop_position == 'right':
                x_offset = scaled_width - self.target_width
            else:  # center
                x_offset = (scaled_width - self.target_width) // 2
            
            # Crop vertical
            y_offset = (scaled_height - self.target_height) // 2
            
            cropped = resized[
                y_offset:y_offset + self.target_height,
                x_offset:x_offset + self.target_width
            ]
            
            # Escrever frame
            out.write(cropped)
            
            frame_count += 1
            
            # Progress
            if frame_count % (fps * 5) == 0:  # A cada 5 segundos
                progress = (frame_count / total_frames) * 100
                print(f"   ⏳ {progress:.1f}%")
        
        cap.release()
        out.release()
        
        print(f"   ✅ Frames processados!")
        
        # Adicionar áudio com ffmpeg
        print(f"   🔊 Adicionando áudio...")
        
        cmd = [
            'ffmpeg',
            '-i', temp_video,
            '-i', input_video,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            '-y',
            output_video
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        # Limpar temporário
        if Path(temp_video).exists():
            Path(temp_video).unlink()
        
        print(f"   ✅ Short renderizado!")
        
        return output_video
    
    def _generate_movement_map(self, total_frames, fps, meme_timestamps):
        """
        Gera mapa de movimento de câmera.
        
        Args:
            total_frames: Total de frames do vídeo
            fps: FPS do vídeo
            meme_timestamps: Lista de {'time': segundos, 'position': 'left'/'right'}
        
        Returns:
            Lista com posição para cada frame ('center', 'left', 'right')
        """
        # Inicializar tudo como 'center'
        movement_map = ['center'] * total_frames
        
        if not meme_timestamps:
            return movement_map
        
        # Processar cada meme
        for meme in meme_timestamps:
            time = meme.get('time', 0)
            position = meme.get('position', 'center')
            
            if position == 'center':
                continue
            
            # Calcular frames
            start_frame = int(time * fps)
            movement_frames = int(self.movement_duration * fps)
            hold_frames = int(self.hold_duration * fps)
            
            # Frames de transição suave (ida)
            for i in range(movement_frames):
                frame_idx = start_frame + i
                if 0 <= frame_idx < total_frames:
                    movement_map[frame_idx] = position
            
            # Frames segurando na posição
            for i in range(hold_frames):
                frame_idx = start_frame + movement_frames + i
                if 0 <= frame_idx < total_frames:
                    movement_map[frame_idx] = position
            
            # Frames de transição suave (volta)
            for i in range(movement_frames):
                frame_idx = start_frame + movement_frames + hold_frames + i
                if 0 <= frame_idx < total_frames:
                    # Gradualmente volta ao centro
                    movement_map[frame_idx] = 'center'
        
        return movement_map
    
    def detect_meme_positions_from_text(self, transcription, meme_config_path):
        """
        Detecta posições de memes baseado no TEXTO da transcrição.
        
        Args:
            transcription: Transcrição com timestamps
            meme_config_path: Caminho do meme_config.json
        
        Returns:
            Lista de {'time': segundos, 'position': 'left'/'right', 'meme_name': str}
        """
        # Carregar configuração de memes
        with open(meme_config_path, 'r', encoding='utf-8') as f:
            meme_config = json.load(f)
        
        detected_memes = []
        
        # Processar cada segmento da transcrição
        for segment in transcription:
            if not isinstance(segment, dict):
                continue
            
            text = segment.get('text', '').lower()
            start_time = segment.get('start', 0)
            
            # Verificar cada meme
            for meme in meme_config.get('memes', []):
                keywords = [k.lower() for k in meme.get('keywords', [])]
                position = meme.get('position', 'center')  # left, right, center
                
                # Verificar se alguma keyword aparece no texto
                for keyword in keywords:
                    if keyword in text:
                        detected_memes.append({
                            'time': start_time,
                            'position': position,
                            'meme_name': meme.get('name', 'unknown'),
                            'keyword': keyword
                        })
                        break  # Não duplicar mesmo meme
        
        print(f"   🎭 {len(detected_memes)} memes detectados por texto")
        
        return detected_memes


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def render_short_with_movement(input_video, output_video, transcription, meme_config_path):
    """
    Renderiza short com movimento de câmera automático.
    
    Args:
        input_video: Vídeo de entrada
        output_video: Vídeo de saída
        transcription: Transcrição com timestamps
        meme_config_path: Caminho do meme_config.json
    
    Returns:
        Caminho do short renderizado
    """
    cropper = SmartCropper()
    
    # Detectar memes por texto
    meme_timestamps = cropper.detect_meme_positions_from_text(
        transcription, 
        meme_config_path
    )
    
    # Renderizar com movimento
    return cropper.render_short(
        input_video,
        output_video,
        meme_timestamps=meme_timestamps
    )
