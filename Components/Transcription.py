# Components/Transcription.py
"""
=============================================================================
TRANSCRIÇÃO DE ÁUDIO COM WHISPER
=============================================================================

O QUE FAZ:
  Usa faster-whisper para transcrever o áudio em português.
  Retorna lista de [palavra, start, end] — timestamps palavra por palavra.

POR QUE PALAVRA POR PALAVRA:
  Necessário para legendas sincronizadas e para o LLM localizar momentos
  exatos (setup_start, reaction_end) na transcrição.

ALTERAÇÕES:
  - Nenhuma alteração; já funcionava bem
  - device="cpu" e compute_type="int8" para compatibilidade

O QUE AINDA PODE SER FEITO:
  - Usar GPU (device="cuda") se disponível para lives longas
  - Modelo "medium" ou "large" para melhor precisão em áudio ruim
  - Cache do modelo para não recarregar a cada execução
  - Detectar idioma automaticamente
=============================================================================
"""

from faster_whisper import WhisperModel


def transcribeAudio(audio_path):
    """
    Transcreve o áudio e retorna lista de tuplas:
    [(palavra1, start1, end1), (palavra2, start2, end2), ...]
    """
    try:
        print("🎤 Transcrevendo áudio (PT-BR + timestamps por palavra)...")

        # Modelo base: bom equilíbrio velocidade/qualidade
        # int8: menor uso de memória, compatível com CPU
        model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

        segments, info = model.transcribe(
            audio=audio_path,
            language="pt",
            task="transcribe",
            beam_size=5,
            vad_filter=True,       # Remove silêncios
            word_timestamps=True,  # Crucial para legendas e LLM
            condition_on_previous_text=False
        )

        results = []
        for seg in segments:
            if not seg.words:
                continue
            for w in seg.words:
                if w.word.strip():
                    results.append([w.word.strip(), w.start, w.end])

        print(f"✅ Transcrição: {len(results)} palavras")
        return results

    except Exception as e:
        print("❌ ERRO NA TRANSCRIÇÃO:", e)
        return []
