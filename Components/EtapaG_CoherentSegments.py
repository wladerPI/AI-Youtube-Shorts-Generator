# Components/EtapaG_CoherentSegments.py
"""
=============================================================================
EXPANSÃO DE HIGHLIGHTS PARA BLOCOS COERENTES
=============================================================================

O QUE FAZ:
  Recebe highlights da IA (start, end) e EXPANDE para incluir frases completas.
  Usa a transcrição palavra-por-palavra para encontrar o início e fim das
  falas que cruzam o intervalo. Evita cortar frases no meio.

POR QUE É NECESSÁRIO:
  O LLM retorna momentos aproximados. Pode cortar "eu estava pensando em..." no
  meio. Esta função alinha com os limites reais da transcrição.

ALTERAÇÕES:
  - gap_tolerance e context_padding usados pelo SegmentSelectorLLM
  - max_duration agora aceita 180 (3min)

O QUE AINDA PODE SER FEITO:
  - Detectar limites de sentenças (pontuação) para cortes mais naturais
  - Expandir para incluir respirações/pausas curtas
=============================================================================
"""

def merge_coherent_segments(
    transcriptions,
    highlights,
    min_duration=20,
    max_duration=120,
    gap_tolerance=1.6,
    context_padding=2.0
):
    """
    Para cada highlight, encontra as falas relacionadas na transcrição e
    expande o bloco para incluir frases completas. Respeita gap_tolerance
    (se gap entre falas <= 1.6s, considera mesma frase).
    """
    refined = []

    for h in highlights:
        raw_start = float(h["start"]) - context_padding
        raw_end = float(h["end"]) + context_padding
        raw_start = max(0, raw_start)

        # Palavras/falas que cruzam o intervalo do highlight
        related = [
            (text, start, end)
            for text, start, end in transcriptions
            if end >= raw_start and start <= raw_end
        ]

        if not related:
            continue

        block_start = related[0][1]
        block_end = related[-1][2]

        # Expande enquanto as falas forem contínuas (gap pequeno)
        for i in range(1, len(related)):
            gap = related[i][1] - related[i - 1][2]
            if gap <= gap_tolerance:
                block_end = related[i][2]
            else:
                break

        duration = block_end - block_start

        # Se ainda curto, tenta expandir mais (5s antes/depois)
        if duration < min_duration:
            for text, start, end in transcriptions:
                if start < block_start and (block_start - start) <= 5:
                    block_start = start
                if end > block_end and (end - block_end) <= 5:
                    block_end = end
            duration = block_end - block_start

        if duration < min_duration:
            continue

        if duration > max_duration:
            block_end = block_start + max_duration

        refined.append({
            "start": round(block_start, 2),
            "end": round(block_end, 2),
            "reason": h.get("reason", "")
        })

    return refined
