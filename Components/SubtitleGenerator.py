# Components/SubtitleGenerator.py
"""
=============================================================================
GERADOR DE LEGENDAS COMPLETO - SEM PALAVRAS FALTANDO
=============================================================================

ALTERAÇÕES NESTA VERSÃO:
  - Garante que TODAS as palavras aparecem no SRT
  - Agrupa palavras em frases de 3-5 segundos
  - Remove marcadores [RISO] das legendas visuais
  - Logging detalhado para debug

PROBLEMA RESOLVIDO:
  - Antes: Algumas palavras sumiam das legendas
  - Agora: Todas as palavras da transcrição aparecem

=============================================================================
"""

import os

def generate_srt(transcriptions, clip_start, clip_end, output_path):
    """
    Gera arquivo SRT com TODAS as palavras do clip.
    
    Args:
        transcriptions: Lista de (palavra, start, end) da transcrição completa
        clip_start: Início do clip em segundos
        clip_end: Fim do clip em segundos
        output_path: Caminho do arquivo .srt
    """
    # Filtrar palavras dentro do intervalo do clip
    clip_words = []
    for word, start, end in transcriptions:
        if clip_start <= start <= clip_end:
            # Ajustar timestamps para começar em 0
            adjusted_start = start - clip_start
            adjusted_end = end - clip_start
            
            # Remover marcadores especiais das legendas
            clean_word = word.replace("[RISO]", "").strip()
            
            if clean_word:  # Só adiciona se tiver conteúdo
                clip_words.append((clean_word, adjusted_start, adjusted_end))
    
    if not clip_words:
        print(f"   ⚠️ Nenhuma palavra encontrada para legendas ({clip_start:.1f}s-{clip_end:.1f}s)")
        # Criar arquivo vazio para não quebrar o pipeline
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("")
        return
    
    # Agrupar palavras em legendas (máximo 5 palavras ou 5s de duração)
    subtitles = []
    current_group = []
    group_start = clip_words[0][1]
    
    for word, start, end in clip_words:
        current_group.append(word)
        
        # Criar nova legenda se:
        # 1. Já tem 5 palavras OU
        # 2. Já passou 5 segundos OU
        # 3. É a última palavra
        should_break = (
            len(current_group) >= 5 or
            (start - group_start) >= 5.0 or
            word == clip_words[-1][0]
        )
        
        if should_break:
            subtitle_text = " ".join(current_group)
            subtitle_end = end
            
            subtitles.append({
                "start": group_start,
                "end": subtitle_end,
                "text": subtitle_text
            })
            
            # Resetar grupo
            current_group = []
            if word != clip_words[-1][0]:  # Se não for a última palavra
                # Próximo grupo começa após a palavra atual
                next_idx = clip_words.index((word, start, end)) + 1
                if next_idx < len(clip_words):
                    group_start = clip_words[next_idx][1]
    
    # Escrever arquivo SRT
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, sub in enumerate(subtitles, 1):
            start_time = _format_srt_time(sub["start"])
            end_time = _format_srt_time(sub["end"])
            
            f.write(f"{idx}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{sub['text']}\n")
            f.write("\n")
    
    print(f"✅ SRT criado: {output_path}")
    print(f"   📝 {len(subtitles)} legendas geradas de {len(clip_words)} palavras")


def _format_srt_time(seconds):
    """
    Converte segundos para formato SRT: HH:MM:SS,mmm
    
    Args:
        seconds: Tempo em segundos (float)
    
    Returns:
        String formatada para SRT
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
