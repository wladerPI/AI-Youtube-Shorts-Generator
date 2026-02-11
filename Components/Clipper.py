# Components/Clipper.py

from Components.RetentionScore import calculate_retention_score
from Components.ViralScore import calculate_viral_score
from Components.SilenceCutter import get_non_silent_segments
from Components.PipelineConfig import get_pipeline_config


def select_best_segments(
    transcript,
    audio_path,
    mode="LIVE"
):
    """
    FUNÇÃO CENTRAL DO PROJETO

    Retorna SEMPRE:
    [
      {"start": float, "end": float, "score": int},
      ...
    ]
    """

    print("✂️ Clipper.select_best_segments iniciado")

    config = get_pipeline_config(mode)

    MAX_SHORTS = config["MAX_SHORTS"]
    MIN_RETENTION = config["MIN_RETENTION"]
    MIN_VIRAL = config["MIN_VIRAL"]

    # --------------------------------------------------
    # 1️⃣ Detecta segmentos SEM silêncio
    # --------------------------------------------------
    segments = get_non_silent_segments(audio_path)

    if not segments:
        print("⚠️ Nenhum segmento válido encontrado")
        return []

    final_segments = []

    # --------------------------------------------------
    # 2️⃣ Score por segmento
    # --------------------------------------------------
    for seg in segments:
        start = seg["start"]
        end = seg["end"]

        retention = calculate_retention_score(transcript, start, end)
        viral = calculate_viral_score(transcript, start, end)

        if retention < MIN_RETENTION or viral < MIN_VIRAL:
            continue

        score = int((retention * 0.6) + (viral * 0.4))

        final_segments.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "score": score
        })

    # --------------------------------------------------
    # 3️⃣ Ordena e limita
    # --------------------------------------------------
    final_segments.sort(key=lambda x: x["score"], reverse=True)

    final_segments = final_segments[:MAX_SHORTS]

    print(f"✅ {len(final_segments)} segmentos selecionados")

    return final_segments
