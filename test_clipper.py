from moviepy.editor import VideoFileClip
from Components.Edit import smart_vertical_crop
from Components.ViralScore import calculate_viral_score
from Components.RetentionScore import calculate_retention_metrics


def run_test():
    input_video = "input.mp4"
    output_video = "SHORT_TEST.mp4"

    start = 0
    end = 18
    reason = "meme reação rage"

    viral = calculate_viral_score(start, end, reason)
    retention = calculate_retention_metrics([80, 78, 76, 75, 74, 73])

    print("Viral:", viral)
    print("Retention:", retention)

    clip = VideoFileClip(input_video).subclip(start, end)

    smart_vertical_crop(
        input_clip=clip,
        highlight_reason=reason,
        output_path=output_video
    )

    print("✅ SHORT GERADO")


if __name__ == "__main__":
    run_test()
