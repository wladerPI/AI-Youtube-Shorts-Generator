# run_pipeline_PROFESSIONAL_V2.py
"""
=============================================================================
PIPELINE PROFISSIONAL V2 - SISTEMA COMPLETO COM MEMES
=============================================================================

🎯 NOVIDADES:
1. ✅ MemeScorer - detecta palavras dos memes
2. ✅ TranscriptionValidator - verifica qualidade
3. ✅ ClipSelector V2 - prioriza memes
4. ✅ ProfileManager V2 - aprendizado multi-perfil
5. ✅ Sistema de pontuação profissional

🚀 USO:
python run_pipeline_PROFESSIONAL_V2.py input/live_cortado.mp4 10 --profile lives_do_11closed

=============================================================================
"""

import sys
import os
from pathlib import Path
import time
import subprocess

# Imports dos componentes
from Components.Transcription import transcribeAudio
from Components.AudioAnalyzer import analyze_audio
from Components.ContextAnalyzer import analyze_context
from Components.MemeScorer import score_moments_with_memes
from Components.TranscriptionValidator import validate_transcription
from Components.ClipSelector_V2 import select_clips_v2
from Components.ProfileManager_V2 import load_profile
from Render.VerticalCropper import render_vertical_video


class PipelineProfessionalV2:
    """Pipeline profissional V2 com memes."""
    
    def __init__(self, input_video, max_shorts=50, profile_name="default"):
        self.input_video = input_video
        self.max_shorts = max_shorts
        self.profile_name = profile_name
        self.session = self._generate_session_id()
        
        # Carregar perfil
        try:
            self.profile = load_profile(profile_name)
            self.profile.start_new_live()
        except Exception as e:
            print(f"⚠️ Erro ao carregar perfil: {e}")
            self.profile = None
        
        print("=" * 70)
        print("🎯 PIPELINE PROFISSIONAL V2 - COM MEMES E APRENDIZADO")
        print("=" * 70)
        print(f"Vídeo: {input_video}")
        print(f"Shorts alvo: {max_shorts}")
        print(f"Perfil: {profile_name}")
        print(f"Session: {self.session}")
        print("=" * 70)
    
    def _generate_session_id(self):
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def run(self):
        """Executa pipeline completo."""
        start_time = time.time()
        
        try:
            # PASSO 1: Extrair áudio
            print("\n📊 PASSO 1/7: Extraindo áudio...")
            audio_file = self._extract_audio()
            
            # PASSO 2: Transcrever
            print("\n🎤 PASSO 2/7: Transcrevendo...")
            transcription = self._transcribe_audio(audio_file)
            
            # PASSO 2.5: Validar transcrição (NOVO!)
            print("\n📋 PASSO 2.5/7: Validando transcrição...")
            validation = validate_transcription(transcription)
            
            # PASSO 3: Analisar áudio
            print("\n🎵 PASSO 3/7: Analisando áudio...")
            audio_moments = analyze_audio(audio_file, transcription)
            
            # PASSO 4: Analisar contexto
            print("\n🤖 PASSO 4/7: Analisando contexto...")
            video_duration_min = self._get_video_duration()
            context_moments = analyze_context(transcription, video_duration_min)
            
            # PASSO 5: Pontuar memes (NOVO!)
            print("\n🎭 PASSO 5/7: Pontuando memes...")
            all_moments = audio_moments + context_moments
            meme_moments = score_moments_with_memes(all_moments, transcription)
            
            # PASSO 6: Selecionar clips V2 (NOVO!)
            print("\n🎬 PASSO 6/7: Selecionando clips...")
            
            # Obter thresholds do perfil
            thresholds = self.profile.get_optimal_thresholds() if self.profile else None
            
            selected_clips = select_clips_v2(
                audio_moments=audio_moments,
                context_moments=context_moments,
                meme_moments=meme_moments,
                max_clips=self.max_shorts,
                profile_thresholds=thresholds
            )
            
            # PASSO 7: Renderizar
            print(f"\n🎥 PASSO 7/7: Renderizando {len(selected_clips)} shorts...")
            self._render_shorts(selected_clips)
            
            # Atualizar perfil
            if self.profile:
                self.profile.add_shorts_generated(len(selected_clips))
                self.profile.save()
            
            # Finalizar
            total_time = time.time() - start_time
            print("\n" + "=" * 70)
            print(f"✅ PIPELINE V2 COMPLETO EM {total_time/60:.1f} MINUTOS!")
            print(f"   Shorts gerados: {len(selected_clips)}")
            print(f"   Pasta: output/shorts_{self.session}/")
            print(f"\n   📝 PRÓXIMO PASSO:")
            print(f"   python review_shorts.py output/shorts_{self.session}/ --profile {self.profile_name}")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
    
    def _extract_audio(self):
        """Extrai áudio."""
        audio_file = f"audio_{self.session}.wav"
        
        cmd = [
            'ffmpeg',
            '-i', self.input_video,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y',
            audio_file
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(audio_file):
            print(f"   ✅ Áudio extraído: {audio_file}")
            return audio_file
        else:
            raise Exception("Falha na extração de áudio")
    
    def _transcribe_audio(self, audio_file):
        """Transcreve áudio."""
        return transcribeAudio(audio_file)
    
    def _get_video_duration(self):
        """Obtém duração do vídeo."""
        import cv2
        cap = cv2.VideoCapture(self.input_video)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration_min = (total_frames / fps) / 60
        cap.release()
        return duration_min
    
    def _render_shorts(self, clips):
        """Renderiza shorts."""
        output_dir = Path(f"output/shorts_{self.session}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, clip in enumerate(clips, 1):
            reasons = ' | '.join(clip.get('reasons', []))[:50]
            meme_info = f" | 🎭 {len(clip.get('meme_names', []))} memes" if clip.get('meme_names') else ""
            
            print(f"\n   [{i}/{len(clips)}] {reasons}{meme_info}...")
            print(f"      Duração: {clip['duration']:.0f}s | Score: {clip['score']:.2f} | Meme: {clip.get('meme_score', 0):.2f}")
            
            if clip.get('meme_names'):
                print(f"      Memes: {', '.join(clip['meme_names'][:3])}")
            
            output_file = output_dir / f"short_{i:03d}.mp4"
            temp_segment = f"temp_segment_{i}.mp4"
            
            try:
                # Extrair segmento COM ÁUDIO
                self._extract_segment(
                    self.input_video,
                    temp_segment,
                    clip['start'],
                    clip['end']
                )
                
                # Renderizar vertical
                render_vertical_video(
                    video_in=temp_segment,
                    video_out=str(output_file)
                )
                
                print(f"      ✅ {output_file.name}")
            
            except Exception as e:
                print(f"      ❌ Erro: {e}")
            
            finally:
                if os.path.exists(temp_segment):
                    try:
                        os.remove(temp_segment)
                    except:
                        pass
    
    def _extract_segment(self, input_video, output_file, start_time, end_time):
        """Extrai segmento COM ÁUDIO."""
        duration = end_time - start_time
        
        cmd = [
            'ffmpeg',
            '-ss', str(start_time),
            '-i', input_video,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            output_file
        ]
        
        result = subprocess.run(
            cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            print(f"      ⚠️ Aviso FFmpeg: {result.stderr[:100]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python run_pipeline_PROFESSIONAL_V2.py <video.mp4> [max_shorts] [--profile nome]")
        print("\nExemplo:")
        print("  python run_pipeline_PROFESSIONAL_V2.py input/live.mp4 50")
        print("  python run_pipeline_PROFESSIONAL_V2.py input/live.mp4 50 --profile lives_do_11closed")
        sys.exit(1)
    
    input_video = sys.argv[1]
    max_shorts = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 50
    
    # Extrair perfil
    profile_name = "default"
    if "--profile" in sys.argv:
        idx = sys.argv.index("--profile")
        if idx + 1 < len(sys.argv):
            profile_name = sys.argv[idx + 1]
    
    if not os.path.exists(input_video):
        print(f"❌ Vídeo não encontrado: {input_video}")
        sys.exit(1)
    
    pipeline = PipelineProfessionalV2(input_video, max_shorts, profile_name)
    pipeline.run()
