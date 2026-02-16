# Components/Transcription.py
"""
=============================================================================
TRANSCRIÇÃO MELHORADA COM DETECÇÃO DE RISADAS
=============================================================================

ALTERAÇÕES NESTA VERSÃO:
  - Detecta picos de áudio (risadas, gritos)
  - Adiciona marcadores "[RISO]" na transcrição
  - Ajuda o GPT a identificar momentos engraçados

COMO FUNCIONA:
  1. Whisper transcreve o áudio
  2. Analisa amplitude do áudio para detectar picos
  3. Marca momentos com volume alto como possíveis risadas
  4. Retorna transcrição enriquecida

=============================================================================
"""

import os
import whisper
import torch
import numpy as np
import librosa

def transcribeAudio(audio_file):
    """
    Transcreve áudio usando Whisper e detecta risadas/reações por picos de áudio.
    
    Returns:
        Lista de tuplas: (palavra, start_time, end_time)
    """
    print("🎤 Transcrevendo áudio (PT-BR + timestamps por palavra)...")
    
    # Verificar CUDA
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        print("   ⚡ GPU detectada - transcrevendo com CUDA")
    else:
        print("   💻 GPU não detectada - usando CPU (mais lento)")
    
    # Carregar modelo Whisper
    model = whisper.load_model("base", device=device)
    
    # Transcrever com word timestamps
    result = model.transcribe(
        audio_file,
        language="pt",
        word_timestamps=True,
        temperature=0.0,
        condition_on_previous_text=True,
        initial_prompt="Esta é uma live de gameplay com comentários, risadas e reações emocionadas."
    )
    
    # Detectar picos de áudio (possíveis risadas/gritos)
    laugh_times = _detect_audio_peaks(audio_file)
    
    # Extrair palavras com timestamps
    transcriptions = []
    for segment in result["segments"]:
        if "words" not in segment:
            continue
            
        for word_data in segment["words"]:
            word = word_data.get("word", "").strip()
            start = float(word_data.get("start", 0))
            end = float(word_data.get("end", 0))
            
            if not word:
                continue
            
            # Verificar se está próximo de um pico de áudio
            if _is_near_laugh(start, laugh_times):
                # Adiciona marcador de riso
                word = f"[RISO] {word}"
            
            transcriptions.append((word, start, end))
    
    print(f"✅ Transcrição: {len(transcriptions)} palavras")
    print(f"   😂 {len(laugh_times)} possíveis risadas/reações detectadas")
    
    return transcriptions


def _detect_audio_peaks(audio_file, threshold_percentile=85):
    """
    Detecta picos de amplitude no áudio (possíveis risadas, gritos, reações).
    
    Args:
        audio_file: Caminho do arquivo de áudio
        threshold_percentile: Percentil para considerar um pico (85 = top 15%)
    
    Returns:
        Lista de timestamps onde há picos de áudio
    """
    try:
        # Carregar áudio
        y, sr = librosa.load(audio_file, sr=16000)
        
        # Calcular envelope de amplitude (RMS)
        hop_length = sr // 10  # 0.1s de resolução
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        
        # Calcular threshold dinâmico
        threshold = np.percentile(rms, threshold_percentile)
        
        # Encontrar picos
        peak_frames = np.where(rms > threshold)[0]
        
        # Converter frames para timestamps
        peak_times = librosa.frames_to_time(peak_frames, sr=sr, hop_length=hop_length)
        
        # Agrupar picos próximos (< 2s de distância)
        grouped_peaks = []
        if len(peak_times) > 0:
            current_peak = peak_times[0]
            for t in peak_times[1:]:
                if t - current_peak > 2.0:  # Gap de 2s
                    grouped_peaks.append(current_peak)
                    current_peak = t
            grouped_peaks.append(current_peak)
        
        return grouped_peaks
        
    except Exception as e:
        print(f"   ⚠️ Erro ao detectar picos de áudio: {e}")
        return []


def _is_near_laugh(timestamp, laugh_times, tolerance=1.5):
    """
    Verifica se um timestamp está próximo de um pico de áudio.
    
    Args:
        timestamp: Tempo da palavra
        laugh_times: Lista de tempos onde há picos
        tolerance: Distância máxima em segundos
    
    Returns:
        True se estiver próximo de um pico
    """
    for laugh_time in laugh_times:
        if abs(timestamp - laugh_time) <= tolerance:
            return True
    return False
