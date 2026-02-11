from Components.EtapaJ_RemoveSilence import remove_silence

input_video = "teste.mp4"
output_video = "teste_sem_silencio.mp4"

remove_silence(
    video_in=input_video,
    video_out=output_video
)

print("✅ TESTE FINALIZADO")
