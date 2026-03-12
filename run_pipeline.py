# run_pipeline.py
"""
Pipeline V3 - Sistema Completo Integrado
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import subprocess
import json

from Components.Transcription import transcribe_audio
from Components.AudioAnalyzer import AudioAnalyzer
from Components.ContextAnalyzer import ContextAnalyzer
from Components.ClipSelector import ClipSelector
from Components.TranscriptionValidator import TranscriptionValidator
from Components.ProfileManager import ProfileManagerV3
from Components.VideoOptimizer import VideoOptimizer
from Components.SubtitleGenerator import SubtitleGenerator
from Render.SmartCropper import SmartCropper


def extract_audio(video_path, audio_path):
    """Extrai áudio do vídeo."""
    print("🎵 Extraindo áudio...")
    
    cmd = [
        'ffmpeg',
        '-i', str(video_path),
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        '-ac', '1',
        '-y',
        str(audio_path)
    ]
    
    subprocess.run(cmd, capture_output=True)
    print("   ✅ Áudio extraído!")
    
    return audio_path


def get_video_duration(video_path):
    """Obtém duração do vídeo em minutos."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'json',
        str(video_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    try:
        data = json.loads(result.stdout)
        duration_sec = float(data['format']['duration'])
        return duration_sec / 60.0
    except:
        return 0


def extract_segment(video_path, start_time, duration, output_path):
    """Extrai segmento do vídeo."""
    cmd = [
        'ffmpeg',
        '-i', str(video_path),
        '-ss', str(start_time),
        '-t', str(duration),
        '-c', 'copy',
        '-y',
        str(output_path)
    ]
    
    subprocess.run(cmd, capture_output=True)
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Pipeline V3 - Geração de Shorts')
    parser.add_argument('video', type=str, help='Vídeo de entrada')
    parser.add_argument('num_shorts', type=int, help='Número de shorts a gerar')
    parser.add_argument('--profile', type=str, default='default', help='Nome do perfil')
    parser.add_argument('--no-optimize', action='store_true', help='Desabilitar otimização')
    parser.add_argument('--no-subtitles', action='store_true', help='Desabilitar legendas')
    parser.add_argument('--no-movement', action='store_true', help='Desabilitar movimento de câmera')
    
    args = parser.parse_args()
    
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"❌ Vídeo não encontrado: {video_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("🚀 PIPELINE V3 - MELHOR GERADOR DE SHORTS DO MUNDO")
    print("=" * 70)
    print(f"📹 Vídeo: {video_path.name}")
    print(f"🎯 Shorts: {args.num_shorts}")
    print(f"👤 Perfil: {args.profile}")
    print("=" * 70)
    
    profile_manager = ProfileManagerV3()
    profile = profile_manager.load_profile(args.profile)
    
    print("\n" + profile_manager.get_config_summary(args.profile))
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path('output') / f'shorts_{timestamp}'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Output: {output_dir}")
    
    video_duration_min = get_video_duration(video_path)
    
    # =========================================================================
    # PASSO 1: TRANSCRIÇÃO
    # =========================================================================
    print("\n" + "=" * 70)
    print("PASSO 1/7: TRANSCRIÇÃO")
    print("=" * 70)
    
    audio_path = output_dir / 'audio.wav'
    extract_audio(video_path, audio_path)
    
    transcription = transcribe_audio(str(audio_path))
    
    validator = TranscriptionValidator()
    validation_result = validator.validate(transcription)
    quality_score = validation_result.get('quality_score', 0)
    print(f"   📊 Qualidade da transcrição: {quality_score}/100")
    
    if quality_score < 50:
        print("   ⚠️  Qualidade baixa! Resultados podem não ser ideais.")
    
    # =========================================================================
    # PASSO 2: ANÁLISE
    # =========================================================================
    print("\n" + "=" * 70)
    print("PASSO 2/7: ANÁLISE")
    print("=" * 70)
    
    audio_analyzer = AudioAnalyzer(str(audio_path))
    audio_features = audio_analyzer.analyze()
    
    context_analyzer = ContextAnalyzer(transcription, video_duration_min)
    context_analysis = context_analyzer.analyze()
    
    # Criar lista de meme_events
    meme_events = []
    
    # Extrair memes dos highlights
    if context_analysis and 'highlights' in context_analysis:
        for highlight in context_analysis['highlights']:
            if 'meme' in highlight.get('reason', '').lower():
                meme_events.append({
                    'start_time': highlight['start_time'],
                    'duration': highlight.get('duration', 45),
                    'score': highlight['score'],
                    'meme_name': highlight.get('reason', 'unknown'),
                    'transcription': highlight.get('transcription', [])
                })
    
    print(f"   🎭 {len(meme_events)} eventos de memes detectados")
    
    # =========================================================================
    # PASSO 3: SELEÇÃO
    # =========================================================================
    print("\n" + "=" * 70)
    print("PASSO 3/7: SELEÇÃO DE CLIPS")
    print("=" * 70)
    
    selector = ClipSelector(profile)
    selected_clips = selector.select_clips(
        audio_features,
        context_analysis,
        meme_events,
        num_clips=args.num_shorts
    )
    
    print(f"   ✅ {len(selected_clips)} clips selecionados")
    
    if not selected_clips:
        print("\n❌ Nenhum clip selecionado!")
        sys.exit(1)
    
    # =========================================================================
    # PASSOS 4-7: PROCESSAMENTO DE CADA CLIP
    # =========================================================================
    
    optimizer = VideoOptimizer(
        speed_factor=profile['video']['speed_factor']
    ) if not args.no_optimize else None
    
    cropper = SmartCropper() if not args.no_movement else None
    
    subtitle_gen = SubtitleGenerator() if not args.no_subtitles else None
    
    for i, clip in enumerate(selected_clips, 1):
        print("\n" + "=" * 70)
        print(f"PROCESSANDO CLIP {i}/{len(selected_clips)}")
        print("=" * 70)
        
        print(f"\n[4/7] Extraindo segmento...")
        segment_path = output_dir / f'segment_{i:03d}.mp4'
        extract_segment(
            video_path,
            clip['start_time'],
            clip['duration'],
            segment_path
        )
        
        if optimizer:
            print(f"\n[5/7] Otimizando...")
            optimized_path = output_dir / f'optimized_{i:03d}.mp4'
            optimizer.optimize_video(str(segment_path), str(optimized_path))
            current_video = optimized_path
        else:
            current_video = segment_path
        
        print(f"\n[6/7] Renderizando...")
        short_path = output_dir / f'short_{i:03d}.mp4'
        
        if cropper and profile['video']['camera_movement_enabled']:
            meme_config_path = 'meme_templates/meme_config.json'
            cropper.render_short(
                str(current_video),
                str(short_path),
                meme_timestamps=cropper.detect_meme_positions_from_text(
                    clip.get('transcription', []),
                    meme_config_path
                )
            )
        else:
            from Render.VerticalCropper import render_vertical_crop
            render_vertical_crop(str(current_video), str(short_path))
        
        if subtitle_gen and profile['subtitles']['enabled']:
            print(f"\n[7/7] Gerando legendas...")
            
            if profile['subtitles']['generate_srt']:
                srt_path = short_path.with_suffix('.srt')
                subtitle_gen.generate_srt(
                    clip.get('transcription', []),
                    str(srt_path)
                )
            
            if profile['subtitles']['generate_ass']:
                ass_path = short_path.with_suffix('.ass')
                subtitle_gen.generate_ass(
                    str(srt_path),
                    str(ass_path),
                    style=profile['subtitles']['style']
                )
        
        if segment_path.exists() and segment_path != current_video:
            segment_path.unlink()
        if current_video != short_path and current_video.exists():
            current_video.unlink()
        
        print(f"   ✅ Short {i} completo!")
    
    # =========================================================================
    # FINALIZAÇÃO
    # =========================================================================
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETO!")
    print("=" * 70)
    print(f"\n📁 Shorts gerados em: {output_dir}")
    print(f"🎬 Total: {len(selected_clips)} shorts")
    print("\n💡 Próximo passo: Revisar shorts com:")
    print(f"   python review_shorts.py {output_dir} --profile {args.profile}")
    print("=" * 70)


if __name__ == '__main__':
    main()
