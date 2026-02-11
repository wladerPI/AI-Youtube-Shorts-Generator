from moviepy.editor import VideoFileClip

def extract_best_thumbnail(video_path, time_sec, output_image):
    clip = VideoFileClip(video_path)
    clip.save_frame(output_image, t=time_sec)
    clip.close()
