# Components/context_builder.py
"""
=============================================================================
CONSTRUTOR DE CONTEXTO COMPLETO
=============================================================================

O QUE FAZ:
  - Expande clips para incluir setup completo
  - Garante que não corta no meio de frase/ação
  - Adiciona margem de segurança
  - Valida duração mínima/máxima

POR QUE EXISTE:
  - Shorts sem contexto não são engraçados
  - Precisa do SETUP + PUNCHLINE + REAÇÃO
  - Espectador precisa entender sem ver o resto

COMO USAR:
  segments = build_context(segments, transcriptions)

=============================================================================
"""

def build_context_for_segments(segments, transcriptions, min_duration=45, max_duration=180):
    """
    Expande segmentos para ter contexto completo.
    
    Args:
        segments: Lista de dicts com start, end, reason
        transcriptions: Lista de (palavra, start, end)
        min_duration: Duração mínima em segundos
        max_duration: Duração máxima em segundos
    
    Returns:
        Lista de segmentos com contexto expandido
    """
    if not segments or not transcriptions:
        return segments
    
    enhanced_segments = []
    
    for seg in segments:
        start = float(seg["start"])
        end = float(seg["end"])
        
        # Expandir para incluir contexto
        expanded_start, expanded_end = _expand_to_context(
            start, end, transcriptions, min_duration, max_duration
        )
        
        # Validar duração
        duration = expanded_end - expanded_start
        
        if duration < min_duration:
            # Muito curto - tentar expandir mais
            missing = min_duration - duration
            expanded_start = max(0, expanded_start - missing/2)
            expanded_end = expanded_end + missing/2
        
        elif duration > max_duration:
            # Muito longo - cortar mantendo o clímax
            excess = duration - max_duration
            # Cortar mais do início (setup) que do fim (reação)
            expanded_start = expanded_start + (excess * 0.7)
            expanded_end = expanded_end - (excess * 0.3)
        
        enhanced_segments.append({
            "start": expanded_start,
            "end": expanded_end,
            "reason": seg.get("reason", ""),
            "original_start": start,
            "original_end": end,
            "context_added": True
        })
    
    return enhanced_segments


def _expand_to_context(start, end, transcriptions, min_dur, max_dur):
    """
    Expande intervalo para incluir frases completas.
    
    Regras:
    - Não corta no meio de palavra
    - Adiciona 3-5s de margem antes e depois
    - Busca pausas naturais (silêncios)
    """
    # Margem de segurança
    BEFORE_MARGIN = 3.0  # 3s antes do setup
    AFTER_MARGIN = 2.0   # 2s após a reação
    
    # Expandir com margens
    expanded_start = max(0, start - BEFORE_MARGIN)
    expanded_end = end + AFTER_MARGIN
    
    # Ajustar para não cortar palavras
    expanded_start = _align_to_word_start(expanded_start, transcriptions, direction="before")
    expanded_end = _align_to_word_end(expanded_end, transcriptions, direction="after")
    
    # Buscar pausas naturais para começar/terminar
    expanded_start = _find_natural_pause(expanded_start, transcriptions, direction="before")
    expanded_end = _find_natural_pause(expanded_end, transcriptions, direction="after")
    
    return expanded_start, expanded_end


def _align_to_word_start(timestamp, transcriptions, direction="before"):
    """Ajusta timestamp para não cortar palavra no início."""
    for word, start, end in transcriptions:
        if direction == "before":
            # Buscar palavra ANTES ou NO timestamp
            if start <= timestamp <= end:
                return start  # Começar na palavra toda
            elif end < timestamp < start:
                return start  # Pular gap e pegar próxima
        else:
            # Buscar palavra DEPOIS do timestamp
            if start >= timestamp:
                return start
    
    return timestamp


def _align_to_word_end(timestamp, transcriptions, direction="after"):
    """Ajusta timestamp para não cortar palavra no final."""
    for word, start, end in reversed(transcriptions):
        if direction == "after":
            # Buscar palavra DEPOIS ou NO timestamp
            if start <= timestamp <= end:
                return end  # Terminar na palavra toda
            elif start < timestamp < end:
                return end
        else:
            # Buscar palavra ANTES do timestamp
            if end <= timestamp:
                return end
    
    return timestamp


def _find_natural_pause(timestamp, transcriptions, direction="before", gap_threshold=1.0):
    """
    Busca pausa natural (silêncio > 1s) próxima ao timestamp.
    
    Args:
        timestamp: Tempo alvo
        transcriptions: Lista de palavras
        direction: "before" ou "after"
        gap_threshold: Tamanho mínimo do gap em segundos
    
    Returns:
        Timestamp ajustado para começar/terminar em pausa
    """
    # Buscar gaps entre palavras
    for i in range(len(transcriptions) - 1):
        curr_word, curr_start, curr_end = transcriptions[i]
        next_word, next_start, next_end = transcriptions[i + 1]
        
        gap = next_start - curr_end
        
        if gap >= gap_threshold:
            # Encontrou pausa
            gap_middle = curr_end + (gap / 2)
            
            if direction == "before":
                # Quer pausa ANTES do timestamp
                if gap_middle <= timestamp <= gap_middle + 2:
                    return next_start  # Começar após a pausa
            
            else:
                # Quer pausa DEPOIS do timestamp
                if gap_middle - 2 <= timestamp <= gap_middle:
                    return curr_end  # Terminar antes da pausa
    
    return timestamp


def validate_segment_context(segment, transcriptions):
    """
    Valida se um segmento tem contexto adequado.
    
    Returns:
        Dict com análise do contexto
    """
    start = segment["start"]
    end = segment["end"]
    
    # Contar palavras no segmento
    words_in_segment = [
        w for w, s, e in transcriptions
        if start <= s <= end
    ]
    
    # Buscar pausas longas no meio
    long_pauses = 0
    for i in range(len(words_in_segment) - 1):
        gap = words_in_segment[i+1][1] - words_in_segment[i][2]
        if gap > 3.0:
            long_pauses += 1
    
    return {
        "has_words": len(words_in_segment) > 0,
        "word_count": len(words_in_segment),
        "long_pauses": long_pauses,
        "duration": end - start,
        "quality_score": _calculate_context_quality(len(words_in_segment), long_pauses, end - start)
    }


def _calculate_context_quality(word_count, long_pauses, duration):
    """
    Calcula score de qualidade do contexto (0-1).
    
    Fatores:
    - Palavras suficientes (30-100 = ideal)
    - Poucas pausas longas (0-1 = bom)
    - Duração adequada (60-90s = ideal)
    """
    score = 1.0
    
    # Penalizar se muito poucas ou muitas palavras
    if word_count < 20:
        score *= 0.5
    elif word_count > 150:
        score *= 0.7
    
    # Penalizar pausas longas
    if long_pauses > 2:
        score *= 0.6
    
    # Bonificar duração ideal
    if 60 <= duration <= 90:
        score *= 1.2
    elif duration < 45:
        score *= 0.7
    elif duration > 150:
        score *= 0.8
    
    return min(1.0, score)
