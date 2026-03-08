# Components/Transcription_FIXED.py
"""
TRANSCRIÇÃO CORRIGIDA - PROCESSA EM CHUNKS
Evita travamento com áudios longos em CPU
"""

import whisper
import warnings
from pydub import AudioSegment
import os

warnings.filterwarnings("ignore")


def transcribeAudio(audio_path, chunk_duration_min=30):
    """
    Transcreve áudio em chunks para evitar travamento.
    
    Args:
        audio_path: Caminho do áudio
        chunk_duration_min: Duração de cada chunk em minutos
    
    Returns:
        Transcrição completa
    """
    print(f"🎤 Transcrevendo áudio em chunks de {chunk_duration_min} min...")
    print("   💻 Processando em CPU (pode demorar)")
    
    # Carregar modelo
    model = whisper.load_model("base")
    
    # Carregar áudio completo
    audio = AudioSegment.from_wav(audio_path)
    duration_ms = len(audio)
    duration_min = duration_ms / (1000 * 60)
    
    print(f"   📊 Duração total: {duration_min:.1f} minutos")
    
    # Calcular chunks
    chunk_duration_ms = chunk_duration_min * 60 * 1000
    num_chunks = int(duration_ms / chunk_duration_ms) + 1
    
    print(f"   📦 Dividindo em {num_chunks} chunks...")
    
    all_segments = []
    total_words = 0
    total_laughs = 0
    
    for i in range(num_chunks):
        start_ms = i * chunk_duration_ms
        end_ms = min((i + 1) * chunk_duration_ms, duration_ms)
        
        if start_ms >= duration_ms:
            break
        
        print(f"\n   [{i+1}/{num_chunks}] Processando {start_ms/60000:.1f}-{end_ms/60000:.1f} min...")
        
        # Extrair chunk
        chunk = audio[start_ms:end_ms]
        chunk_file = f"temp_chunk_{i}.wav"
        chunk.export(chunk_file, format="wav")
        
        try:
            # Transcrever chunk
            result = model.transcribe(
                chunk_file,
                language="pt",
                task="transcribe",
                word_timestamps=True,
                condition_on_previous_text=True
            )
            
            # Ajustar timestamps (somar offset do chunk)
            offset_seconds = start_ms / 1000
            
            for segment in result.get("segments", []):
                segment["start"] += offset_seconds
                segment["end"] += offset_seconds
                
                if "words" in segment:
                    for word in segment["words"]:
                        word["start"] += offset_seconds
                        word["end"] += offset_seconds
                
                all_segments.append(segment)
            
            # Contar palavras e risadas
            text = result.get("text", "")
            words = len(text.split())
            laughs = text.lower().count("[riso]") + text.lower().count("hahaha") + text.lower().count("kkkk")
            
            total_words += words
            total_laughs += laughs
            
            print(f"      ✅ {words} palavras, {laughs} risadas")
        
        except KeyboardInterrupt:
            print(f"\n      ⚠️ Chunk {i+1} cancelado pelo usuário")
            break
        
        except Exception as e:
            print(f"      ❌ Erro no chunk {i+1}: {e}")
        
        finally:
            # Limpar arquivo temporário
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
    
    print(f"\n✅ Transcrição completa!")
    print(f"   📝 Total: {total_words} palavras")
    print(f"   😂 Total: {total_laughs} risadas detectadas")
    
    return all_segments


# Função de compatibilidade
def transcribe_audio(audio_path):
    """Wrapper para compatibilidade."""
    return transcribeAudio(audio_path)
