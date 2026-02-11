import os
import json
import shutil


def classify_short(score, early_drop):
    if score >= 75 and early_drop < 0.15:
        return "EXCELENTE"
    elif score >= 55:
        return "BOM"
    else:
        return "DESCARTAR"


def analyze_curve(curve):
    early_points = [p for p in curve if p["time"] <= 5]
    if not early_points:
        return 1.0

    start = early_points[0]["attention"]
    end = early_points[-1]["attention"]

    drop = max(0, start - end)
    return drop


def rank_shorts(output_dir):
    results = []

    for file in os.listdir(output_dir):
        if not file.endswith("_retention.json"):
            continue

        path = os.path.join(output_dir, file)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        score = data.get("attention_score", 0)
        curve = data.get("curve", [])

        early_drop = analyze_curve(curve)
        classification = classify_short(score, early_drop)

        base_name = file.replace("_retention.json", ".mp4")

        results.append({
            "video": base_name,
            "score": score,
            "early_drop": round(early_drop, 3),
            "class": classification
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def export_results(results, output_dir):
    ranking_dir = os.path.join(output_dir, "rankings")
    winners_dir = os.path.join(output_dir, "winners")

    os.makedirs(ranking_dir, exist_ok=True)
    os.makedirs(winners_dir, exist_ok=True)

    # JSON
    with open(os.path.join(ranking_dir, "ranking.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # TXT legível
    with open(os.path.join(ranking_dir, "ranking.txt"), "w", encoding="utf-8") as f:
        for r in results:
            f.write(
                f"{r['video']} | SCORE={r['score']} | DROP={r['early_drop']} | {r['class']}\n"
            )

    # Copia só os EXCELENTES
    for r in results:
        if r["class"] == "EXCELENTE":
            src = os.path.join(output_dir, r["video"])
            dst = os.path.join(winners_dir, r["video"])
            if os.path.exists(src):
                shutil.copy2(src, dst)
