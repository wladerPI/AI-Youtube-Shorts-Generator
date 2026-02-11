import json

def export_metadata(
    output_path,
    viral_score,
    movement_intensity,
    camera_path,
    audio_peak_time
):
    metadata = {
        "viral_score": viral_score,
        "movement_intensity": movement_intensity,
        "camera_path": camera_path,
        "audio_peak_time": audio_peak_time
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
