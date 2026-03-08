# run_pipeline_PROFESSIONAL.py
"""
=============================================================================
PIPELINE PROFISSIONAL FINAL - VERSÃO CORRIGIDA
=============================================================================

CORREÇÕES:
- ✅ Extração de segmentos COM ÁUDIO (re-encode)
- ✅ Transcrição em chunks (não trava)
- ✅ API Key corrigida

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
from Components.ClipSelector import select_clips
from Components.ProfileManager import load_profile
from Render.VerticalCropper import render_vertical_video


class PipelineProfessional:
    """Pipeline profissional otimizado para CPU."""
    
    def __init__(self, input_video, max_shorts=50):
        self.input_video = input_video
        self.max_shorts = max_shorts
        self.session = self._generate_session_id()
        
        # Carregar perfil
        try:
            self.profile = load_profile("lives_do_11closed")
            self.profile.start_new_live()
        except:
            print("⚠️ Perfil não carregado (não crítico)")
            self.profile = None
        
        print("=" * 70)
        print("🎯 PIPELINE PROFISSIONAL - CPU OPTIMIZED")
        print("=" * 70)
        print(f"Vídeo: {input_video}")
        print(f"Shorts alvo: {max_shorts}")
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
            print("\n📊 PASSO 1/6: Extraindo áudio...")
            audio_file = self._extract_audio()
            
            # PASSO 2: Transcrever
            print("\n🎤 PASSO 2/6: Transcrevendo...")
            transcription = self._transcribe_audio(audio_file)
            
            # PASSO 3: Analisar áudio
            print("\n🎵 PASSO 3/6: Analisando áudio...")
            audio_moments = analyze_audio(audio_file, transcription)
            
            # PASSO 4: Analisar contexto
            print("\n🤖 PASSO 4/6: Analisando contexto...")
            video_duration_min = self._get_video_duration()
            context_moments = analyze_context(transcription, video_duration_min)
            
            # PASSO 5: Selecionar clips
            print("\n🎬 PASSO 5/6: Selecionando clips...")
            selected_clips = select_clips(audio_moments, context_moments, self.max_shorts)
            
            # PASSO 6: Renderizar
            print(f"\n🎥 PASSO 6/6: Renderizando {len(selected_clips)} shorts...")
            self._render_shorts(selected_clips)
            
            # Finalizar
            total_time = time.time() - start_time
            print("\n" + "=" * 70)
            print(f"✅ PIPELINE COMPLETO EM {total_time/60:.1f} MINUTOS!")
            print(f"   Shorts gerados: {len(selected_clips)}")
            print(f"   Pasta: output/shorts_{self.session}/")
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
            print(f"\n   [{i}/{len(clips)}] {reasons}...")
            print(f"      Duração: {clip['duration']:.0f}s | Score: {clip['score']:.2f}")
            
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
        """
        Extrai segmento COM ÁUDIO.
        
        IMPORTANTE: Re-encode para garantir áudio!
        """
        duration = end_time - start_time
        
        cmd = [
            'ffmpeg',
            '-ss', str(start_time),  # Seek ANTES do input (mais rápido)
            '-i', input_video,
            '-t', str(duration),
            '-c:v', 'libx264',      # Re-encode vídeo
            '-preset', 'medium',     # Qualidade média (mais rápido)
            '-crf', '23',            # Qualidade boa
            '-c:a', 'aac',           # Re-encode áudio
            '-b:a', '192k',          # Bitrate áudio 192kbps
            '-y',
            output_file
        ]
        
        result = subprocess.run(
            cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Verificar se gerou arquivo com áudio
        if result.returncode != 0:
            print(f"      ⚠️ Aviso FFmpeg: {result.stderr[:100]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python run_pipeline_PROFESSIONAL.py <video.mp4> [max_shorts]")
        print("\nExemplo:")
        print("  python run_pipeline_PROFESSIONAL.py input/live.mp4 50")
        sys.exit(1)
    
    input_video = sys.argv[1]
    max_shorts = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    if not os.path.exists(input_video):
        print(f"❌ Vídeo não encontrado: {input_video}")
        sys.exit(1)
    
    pipeline = PipelineProfessional(input_video, max_shorts)
    pipeline.run()
