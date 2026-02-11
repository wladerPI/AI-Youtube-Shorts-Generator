import os
import json
from Components.FaceCrop import crop_to_vertical_with_audio


def rerender_good_shorts(
    ranking_path: str,
    input_dir: str = "clips_vertical",
    output_dir: str = "clips_rerendered",
    aggressive_multiplier: int = 25,
    debug: bool = False
):
    if not os.path.exists(ranking_path):
        print("❌ Ranking não encontrado, rerender ignorado.")
        return []

    with open(ranking_path, "r", encoding="utf-8") as f:
        ranking = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    rerendered = []

    for item in ranking:
        if item.get("class") != "BOM":
            continue

        video_name = item["video"]
        score = item.get("score", 0)

        input_video = os.path.join(input_dir, video_name)
        if not os.path.exists(input_video):
            print(f"⚠️ Vídeo não encontrado: {input_video}")
            continue

        aggressive_score = min(100, score + aggressive_multiplier)

        output_video = os.path.join(
            output_dir,
            video_name.replace(".mp4", "_AGRESSIVO.mp4")
        )

        print(f"\n🔥 RE-RENDER AUTOMÁTICO")
        print(f"🎞️ {video_name}")
        print(f"📈 Score: {score} → {aggressive_score}")

        crop_to_vertical_with_audio(
            input_video=input_video,
            output_video=output_video,
            viral_score=aggressive_score,
            debug=debug,
            debug_overlay=False
        )

        rerendered.append(output_video)

    print(f"\n✅ Re-render finalizado: {len(rerendered)} shorts melhorados")
    return rerendered
