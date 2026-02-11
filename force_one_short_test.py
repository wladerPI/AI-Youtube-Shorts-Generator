import os
from moviepy.editor import VideoFileClip

VIDEO_INPUT = "input/teste.mp4"
OUTPUT_DIR = "clips_vertical"

START_TIME = 5     # segundos
END_TIME = 25      # segundos

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🔥 FORÇANDO 1 SHORT FIXO (SEM IA, SEM JSON)")

print(f"🎯 Corte manual: {START_TIME}s → {END_TIME}s")

video = VideoFileClip(VIDEO_INPUT).subclip(START_TIME, END_TIME)

# Converter para 9:16 (crop central)
w, h = video.size
target_w = int(h * 9 / 16)

x_center = w // 2
x1 = max(0, x_center - target_w // 2)
x2 = min(w, x_center + target_w // 2)

video_vertical = video.crop(x1=x1, x2=x2)

output_path = os.path.join(OUTPUT_DIR, "TEST_FORCED_FIXED.mp4")

video_vertical.write_videofile(
    output_path,
    codec="libx264",
    audio_codec="aac",
    fps=30
)

print(f"✅ SHORT GERADO: {output_path}")
