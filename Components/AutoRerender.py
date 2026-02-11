# Components/AutoRerender.py

from Components.FaceCrop import crop_to_vertical_with_audio

def auto_rerender_if_needed(summary, original_clip, transcript_text):
    """
    Se IA pedir RERENDER:
    - refaz vídeo com câmera mais agressiva
    """

    if summary.get("decision") != "RERENDER":
        return None

    new_output = original_clip.replace(".mp4", "_rerender.mp4")

    print("🔄 AUTO-RERENDER ATIVADO")

    crop_to_vertical_with_audio(
        input_video=original_clip,
        output_video=new_output,
        reason=summary["reason"],
        transcript_text=transcript_text,
        viral_score=summary["viral_score"] + 15,  # bias agressivo
        debug=False
    )

    return new_output
