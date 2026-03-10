# Components/VideoOptimizer.py
"""
=============================================================================
OTIMIZADOR DE VÍDEO PROFISSIONAL
=============================================================================

✨ FEATURES:
- Remove silêncios longos
- Acelera vídeo (1.2x-1.3x)
- Normaliza áudio
- Mantém sincronia perfeita
- Processamento eficiente

=============================================================================
"""

import subprocess
import numpy as np
import re
from pathlib import Path
import json


class VideoOptimizer:
    """Otimiza vídeos para maior engajamento."""
    
    def __init__(self, 
                 silence_threshold=-35,      # dB
                 min_silence_duration=1.0,   # segundos
                 speed_factor=1.25,          # 1.0 = normal, 1.25 = 25% mais rápido
                 keep_silence_padding=0.2):  # segundos de padding
        """
        Inicializa otimizador.
        
        Args:
            silence_threshold: Threshold de silêncio em dB
            min_silence_duration: Duração mínima para considerar silêncio
            speed_factor: Fator de aceleração (1.2 = 20% mais rápido)
            keep_silence_padding: Segundos de silêncio para manter (naturalidade)
        """
        self.silence_threshold = silence_threshold
        self.min_silence_duration = min_silence_duration
        self.speed_factor = speed_factor
        self.keep_silence_padding = keep_silence_padding
    
    def optimize_video(self, input_video, output_video):
        """
        Otimiza vídeo completo.
        
        WORKFLOW:
        1. Remove silêncios longos
        2. Acelera vídeo
        3. Normaliza áudio
        
        Args:
            input_video: Vídeo de entrada
            output_video: Vídeo de saída
        
        Returns:
            Caminho do vídeo otimizado
        """
        print(f"⚡ Otimizando vídeo: {Path(input_video).name}")
        
        # Arquivo temporário
        temp_video = str(Path(output_video).with_stem(Path(output_video).stem + '_temp'))
        
        try:
            # PASSO 1: Remover silêncios
            print(f"   [1/3] Removendo silêncios...")
            no_silence_video = self._remove_silences(input_video, temp_video)
            
            # PASSO 2: Acelerar vídeo
            print(f"   [2/3] Acelerando {self.speed_factor}x...")
            speed_video = self._adjust_speed(no_silence_video, output_video)
            
            # PASSO 3: Normalizar áudio
            print(f"   [3/3] Normalizando áudio...")
            final_video = self._normalize_audio(speed_video, output_video)
            
            # Limpar temporários
            if Path(temp_video).exists():
                Path(temp_video).unlink()
            
            print(f"   ✅ Vídeo otimizado!")
            
            return final_video
        
        except Exception as e:
            print(f"   ❌ Erro na otimização: {e}")
            # Se falhar, retornar vídeo original
            if Path(input_video) != Path(output_video):
                import shutil
                shutil.copy(input_video, output_video)
            return output_video
    
    def _remove_silences(self, input_video, output_video):
        """Remove silêncios longos do vídeo."""
        
        # Detectar silêncios com ffmpeg
        cmd_detect = [
            'ffmpeg',
            '-i', input_video,
            '-af', f'silencedetect=noise={self.silence_threshold}dB:d={self.min_silence_duration}',
            '-f', 'null',
            '-'
        ]
        
        result = subprocess.run(
            cmd_detect,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # Parsear silêncios detectados
        silences = self._parse_silence_output(result.stderr)
        
        if not silences:
            # Sem silêncios longos, copiar vídeo
            import shutil
            shutil.copy(input_video, output_video)
            return output_video
        
        # Criar filtro complexo para remover silêncios
        filter_parts = []
        segments = []
        
        # Obter duração total
        duration = self._get_video_duration(input_video)
        
        # Criar segmentos (partes sem silêncio)
        last_end = 0
        
        for silence in silences:
            start = silence['start']
            end = silence['end']
            
            # Adicionar segmento antes do silêncio
            if start - last_end > 0.1:  # Mínimo 0.1s
                segments.append({
                    'start': last_end,
                    'end': start + self.keep_silence_padding  # Manter um pouco
                })
            
            last_end = max(last_end, end - self.keep_silence_padding)
        
        # Adicionar último segmento
        if duration - last_end > 0.1:
            segments.append({
                'start': last_end,
                'end': duration
            })
        
        # Se muito poucos segmentos, não vale a pena
        if len(segments) <= 1:
            import shutil
            shutil.copy(input_video, output_video)
            return output_video
        
        # Criar filtro de corte
        filter_segments = []
        for i, seg in enumerate(segments):
            filter_segments.append(f"[0:v]trim=start={seg['start']}:end={seg['end']},setpts=PTS-STARTPTS[v{i}]")
            filter_segments.append(f"[0:a]atrim=start={seg['start']}:end={seg['end']},asetpts=PTS-STARTPTS[a{i}]")
        
        # Concatenar segmentos
        v_streams = ''.join(f'[v{i}]' for i in range(len(segments)))
        a_streams = ''.join(f'[a{i}]' for i in range(len(segments)))
        
        concat_filter = f"{v_streams}concat=n={len(segments)}:v=1:a=0[outv];{a_streams}concat=n={len(segments)}:v=0:a=1[outa]"
        
        filter_complex = ';'.join(filter_segments) + ';' + concat_filter
        
        # Aplicar filtro
        cmd_cut = [
            'ffmpeg',
            '-i', input_video,
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-map', '[outa]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            output_video
        ]
        
        subprocess.run(cmd_cut, capture_output=True)
        
        return output_video
    
    def _adjust_speed(self, input_video, output_video):
        """Acelera vídeo mantendo pitch do áudio."""
        
        # Calcular PTS para vídeo e áudio
        video_pts = 1.0 / self.speed_factor
        
        cmd = [
            'ffmpeg',
            '-i', input_video,
            '-filter_complex',
            f'[0:v]setpts={video_pts}*PTS[v];[0:a]atempo={self.speed_factor}[a]',
            '-map', '[v]',
            '-map', '[a]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            output_video
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        return output_video
    
    def _normalize_audio(self, input_video, output_video):
        """Normaliza áudio do vídeo."""
        
        cmd = [
            'ffmpeg',
            '-i', input_video,
            '-af', 'loudnorm=I=-16:LRA=11:TP=-1.5',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            output_video
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        return output_video
    
    def _parse_silence_output(self, stderr_output):
        """Parseia output do silencedetect."""
        silences = []
        
        current_silence = {}
        
        for line in stderr_output.split('\n'):
            if 'silence_start' in line:
                match = re.search(r'silence_start: ([\d.]+)', line)
                if match:
                    current_silence = {'start': float(match.group(1))}
            
            elif 'silence_end' in line and current_silence:
                match = re.search(r'silence_end: ([\d.]+)', line)
                if match:
                    current_silence['end'] = float(match.group(1))
                    silences.append(current_silence)
                    current_silence = {}
        
        return silences
    
    def _get_video_duration(self, video_path):
        """Obtém duração do vídeo."""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        try:
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except:
            # Fallback: usar opencv
            import cv2
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            return frame_count / fps if fps > 0 else 60.0


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def optimize_short(input_video, output_video, speed=1.25):
    """
    Otimiza um short.
    
    Args:
        input_video: Vídeo de entrada
        output_video: Vídeo de saída
        speed: Fator de aceleração (1.25 = 25% mais rápido)
    
    Returns:
        Caminho do vídeo otimizado
    """
    optimizer = VideoOptimizer(speed_factor=speed)
    return optimizer.optimize_video(input_video, output_video)
