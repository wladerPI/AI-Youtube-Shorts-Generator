# Components/TemporalFilter.py
"""
=============================================================================
FILTRO DE DISTÂNCIA TEMPORAL ENTRE SEGMENTOS
=============================================================================

O QUE FAZ:
  Garante que segmentos selecionados tenham distância mínima entre si
  (em segundos). Usa o start do segmento para comparar.
  Ex: min_distance=90 → não coloca dois shorts com menos de 90s de diferença.

POR QUE:
  Evita concentrar vários shorts no mesmo trecho da live. Distribui
  os cortes ao longo da transmissão.

ALTERAÇÕES:
  - run_pipeline usa min_distance=90 (antes 120)

O QUE AINDA PODE SER FEITO:
  - Considerar distribuição uniforme ao longo da live
  - Ponderar por horário (ex: primeiros 30min têm mais hook)
=============================================================================
"""

def filter_by_time_distance(segments, min_distance=180):
    """
    Retorna apenas segmentos cujo start está a pelo menos min_distance
    segundos do start do segmento anterior aceito.
    """
    filtered = []

    for seg in segments:
        if not filtered:
            filtered.append(seg)
            continue

        last = filtered[-1]
        if abs(seg["start"] - last["start"]) >= min_distance:
            filtered.append(seg)

    return filtered
