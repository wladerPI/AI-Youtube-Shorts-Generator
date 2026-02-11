from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.VideoClip import TextClip

from Components.CameraLimits import apply_camera_limits
from Components.CameraLogic import decide_camera_path, get_crop_x
from Components.AudioEvents import detect_audio_peak
from Components.CameraMemory import get_last_camera_state, set_last_camera_state

from Components.RetentionCurve import build_retention_curve
from Components.AttentionScorer import calculate_attention_score

from Components.CameraTimeline import CameraTimeline
from Components.CameraDirector import decide_camera_events

import json


def movement_intensity_from_score(score: int) -> float:
    if score <= 20:
        return 0.4
    elif score <= 40:
        return 0.6
    elif score <= 60:
        return 0.85
    elif score <= 80:
        return 1.2
    else:
        return 1.6


def crop_to_vertical_with_audio(
    input_video: str,
    output_video: str,
    reason: str = "",
    transcript_text: str = "",
    viral_score: int = 0,
    debug: bool = False,
    debug_overlay: bool = False
):
    print("🎥 Criando vídeo vertical (câmera inteligente + diretor cinematográfico)...")

    clip = VideoFileClip(input_video)

    vw, vh = clip.size
    duration = clip.duration
    target_w = int(vh * 9 / 16)

    if target_w > vw:
        raise ValueError("❌ Vídeo muito estreito para 9:16")

    movement_intensity = movement_intensity_from_score(viral_score)

    peak_time = detect_audio_peak(input_video)
    last_state = get_last_camera_state()

    camera_path = decide_camera_path(
        reason=reason,
        transcript_text=transcript_text,
        viral_score=viral_score,
        audio_peak_time=peak_time,
        previous_state=last_state
    )

    raw_positions = [
        get_crop_x(vw, target_w, state)
        for state in camera_path
    ]

    positions = apply_camera_limits(
        video_width=vw,
        crop_width=target_w,
        positions=raw_positions,
        duration=duration
    )

    timeline = CameraTimeline()

    from Components.CameraAIDirector import apply_ai_bias_to_events

    director_events = decide_camera_events(
        transcript_text=transcript_text,
        vw=vw,
        target_w=target_w,
        duration=duration
    )

    director_events = apply_ai_bias_to_events(
        director_events,
        vw,
        target_w
    )
    
    
    from Components.CameraEventCollector import collect_camera_events

    auto_events = collect_camera_events(
        input_video,
        vw,
        target_w
    )

    for e in auto_events:
        timeline.add_event(
            start=e["start"],
            end=e["end"],
            target_x=e["target_x"]
        )

    
    
    for e in director_events:
        timeline.add_event(
            start=e["start"],
            end=e["end"],
            target_x=e["target_x"]
        )

    camera_events_log = []

    def crop_frame(get_frame, t):
        frame = get_frame(t)
        x = timeline.get_x(t, positions[0])
        x = max(0, min(x, vw - target_w))

        cam_state = "CENTER"
        if x < vw * 0.25:
            cam_state = "LEFT"
        elif x > vw * 0.55:
            cam_state = "RIGHT"

        set_last_camera_state(cam_state)

        camera_events_log.append({
            "time": round(t, 3),
            "camera": cam_state
        })

        return frame[0:vh, x:x + target_w]

    vertical = clip.fl(crop_frame)

    # 🔊 ÁUDIO DEFENSIVO
    if clip.audio:
        vertical = vertical.set_audio(clip.audio)

    vertical.write_videofile(
        output_video,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4
    )

    retention_curve = build_retention_curve(
        duration=duration,
        audio_peak_time=peak_time,
        camera_events=camera_events_log,
        viral_score=viral_score
    )

    attention_score = calculate_attention_score(retention_curve)

    with open(output_video.replace(".mp4", "_retention.json"), "w", encoding="utf-8") as f:
        json.dump({
            "attention_score": attention_score,
            "curve": retention_curve
        }, f, indent=2)

    clip.close()
    vertical.close()

    print(f"📈 Retention Score: {attention_score}")
    print("✅ Vídeo finalizado com câmera cinematográfica inteligente")
