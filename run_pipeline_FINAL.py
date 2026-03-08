# run_pipeline_FINAL.py - VERSÃO CORRIGIDA
"""
=============================================================================
PIPELINE FINAL INTEGRADO - CORRIGIDO PARA SEU PROJETO
=============================================================================

CORREÇÕES:
- Usa Transcription.py (não AudioExtraction)
- Usa módulos existentes do projeto
- Mantém toda a lógica profissional

=============================================================================
"""

import sys
import os
from pathlib import Path
import time
from threading import Thread
import json
import subprocess

# Imports dos componentes DO SEU PROJETO
sys.path.append(str(Path(__file__).parent))

from Components.Transcription import transcribeAudio
from Components.LanguageTasks import GetHighlights
from Components.MemeDetectorPro import detect_memes_professional
from Components.ProfileManager import load_profile
from Render.VerticalCropper import render_vertical_video


class PipelineFinal:
    """Pipeline integrado final com máxima qualidade."""
    
    def __init__(self, input_video, max_shorts=50):
        self.input_video = input_video
        self.max_shorts = max_shorts
        self.session = self._generate_session_id()
        
        # Carregar perfil
        try:
            self.profile = load_profile("lives_do_11closed")
        except:
            print("⚠️ Perfil não carregado (não crítico)")
            self.profile = None
        
        print("=" * 70)
        print("PIPELINE FINAL - MÁXIMA QUALIDADE")
        print("=" * 70)
        print(f"Vídeo: {input_video}")
        print(f"Shorts alvo: {max_shorts}")
        print(f"Session: {self.session}")
        print("=" * 70)
    
    def _generate_session_id(self):
        """Gera ID único da sessão."""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def run(self):
        """Executa pipeline completo."""
        start_time = time.time()
        
        # PASSO 1: Extrair áudio
        print("\n📊 PASSO 1/6: Extraindo áudio...")
        audio_file = self._extract_audio()
        
        # PASSO 2 e 3: Análise paralela
        print("\n🔀 PASSOS 2-3: Análise paralela (Áudio + Visual)...")
        print("   Thread 1: Transcrição + GPT")
        print("   Thread 2: Detecção visual profissional")
        
        audio_results = {}
        visual_results = {}
        
        def audio_thread():
            audio_results['data'] = self._analyze_audio(audio_file)
        
        def visual_thread():
            visual_results['data'] = self._analyze_visual()
        
        t1 = Thread(target=audio_thread)
        t2 = Thread(target=visual_thread)
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # PASSO 4: Combinar resultados
        print("\n🔗 PASSO 4/6: Combinando resultados...")
        combined_clips = self._combine_results(
            audio_results['data'],
            visual_results['data']
        )
        
        # PASSO 5: Selecionar melhores
        print("\n⭐ PASSO 5/6: Selecionando melhores clips...")
        selected_clips = self._select_best_clips(combined_clips)
        
        # PASSO 6: Renderizar
        print(f"\n🎬 PASSO 6/6: Renderizando {len(selected_clips)} shorts...")
        self._render_shorts(selected_clips, visual_results['data'])
        
        # Finalizar
        total_time = time.time() - start_time
        print("\n" + "=" * 70)
        print(f"✅ PIPELINE COMPLETO EM {total_time/60:.1f} MINUTOS!")
        print(f"   Shorts gerados: {len(selected_clips)}")
        print(f"   Pasta: output/shorts_{self.session}/")
        print("=" * 70)
    
    def _extract_audio(self):
        """Extrai áudio usando ffmpeg."""
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
        
        print(f"   Executando: ffmpeg...")
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if result.returncode == 0 and os.path.exists(audio_file):
            print(f"   ✅ Áudio extraído: {audio_file}")
            return audio_file
        else:
            print(f"   ❌ Erro ao extrair áudio!")
            raise Exception("Falha na extração de áudio")
    
    def _analyze_audio(self, audio_file):
        """Analisa áudio (transcrição + GPT)."""
        print("      [Áudio] Transcrevendo com Whisper...")
        
        try:
            transcriptions = transcribeAudio(audio_file)
            print(f"      [Áudio] ✅ Transcrição completa")
        except Exception as e:
            print(f"      [Áudio] ❌ Erro na transcrição: {e}")
            return []
        
        print("      [Áudio] Analisando com GPT (79 memes)...")
        
        # Calcular duração do vídeo
        import cv2
        cap = cv2.VideoCapture(self.input_video)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration_min = (total_frames / fps) / 60
        cap.release()
        
        try:
            # Obter highlights do GPT
            highlights = GetHighlights(
                transcript_text=str(transcriptions),
                video_duration_min=duration_min
            )
            print(f"      [Áudio] ✅ {len(highlights)} momentos detectados")
            return highlights
        except Exception as e:
            print(f"      [Áudio] ❌ Erro no GPT: {e}")
            return []
    
    def _analyze_visual(self):
        """Analisa visual (motion + feature matching)."""
        print("      [Visual] Iniciando detecção profissional...")
        
        try:
            meme_events = detect_memes_professional(
                video_path=self.input_video,
                session_id=self.session,
                motion_threshold=0.60,
                match_threshold=0.85
            )
            print(f"      [Visual] ✅ {len(meme_events)} memes detectados")
            return meme_events
        except Exception as e:
            print(f"      [Visual] ❌ Erro: {e}")
            return []
    
    def _combine_results(self, audio_clips, visual_memes):
        """Combina resultados de áudio e visual."""
        combined = []
        
        # Adicionar clips de áudio
        for clip in audio_clips:
            combined.append({
                'start': clip.get('start', 0),
                'end': clip.get('end', 60),
                'reason': clip.get('reason', 'momento detectado'),
                'score': clip.get('score', 1.0),
                'source': 'audio',
                'has_meme': False
            })
        
        # Adicionar eventos visuais
        for meme in visual_memes:
            start = max(0, meme['timestamp'] - 15)
            end = meme['timestamp'] + meme['duration'] + 15
            
            combined.append({
                'start': start,
                'end': end,
                'reason': f"meme visual: {meme['meme_name']}",
                'score': meme['score'] * 1.2,
                'source': 'visual',
                'has_meme': True,
                'meme_data': meme
            })
        
        print(f"   Total combinado: {len(combined)} clips")
        print(f"      Áudio: {len(audio_clips)}")
        print(f"      Visual: {len(visual_memes)}")
        
        return combined
    
    def _select_best_clips(self, clips):
        """Seleciona os melhores clips."""
        if not clips:
            print("   ⚠️ Nenhum clip para selecionar!")
            return []
        
        # Ordenar por score
        clips.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Remover sobreposições
        selected = []
        for clip in clips:
            overlap = False
            for sel in selected:
                if self._clips_overlap(clip, sel):
                    overlap = True
                    break
            
            if not overlap:
                selected.append(clip)
                
                if len(selected) >= self.max_shorts:
                    break
        
        print(f"   Selecionados: {len(selected)}/{len(clips)} clips")
        if selected:
            with_memes = sum(1 for c in selected if c.get('has_meme', False))
            print(f"      Com memes: {with_memes}")
            print(f"      Só áudio: {len(selected) - with_memes}")
        
        return selected
    
    def _clips_overlap(self, clip1, clip2, min_gap=30):
        """Verifica se clips se sobrepõem."""
        return not (clip1['end'] + min_gap < clip2['start'] or 
                   clip2['end'] + min_gap < clip1['start'])
    
    def _render_shorts(self, clips, visual_memes):
        """Renderiza shorts."""
        output_dir = Path(f"output/shorts_{self.session}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, clip in enumerate(clips, 1):
            reason = clip.get('reason', 'clip')[:50]
            print(f"\n   [{i}/{len(clips)}] {reason}...")
            
            output_file = output_dir / f"short_{i:03d}.mp4"
            temp_segment = f"temp_segment_{i}.mp4"
            
            try:
                # Extrair segmento
                self._extract_segment(
                    self.input_video,
                    temp_segment,
                    clip['start'],
                    clip['end']
                )
                
                # Renderizar vertical
                render_vertical_video(
                    video_in=temp_segment,
                    video_out=str(output_file),
                    meme_events=visual_memes if clip.get('has_meme') else None,
                    session_id=self.session
                )
                
                print(f"      ✅ {output_file.name}")
            
            except Exception as e:
                print(f"      ❌ Erro: {e}")
            
            finally:
                # Limpar temp
                if os.path.exists(temp_segment):
                    try:
                        os.remove(temp_segment)
                    except:
                        pass
    
    def _extract_segment(self, input_video, output_file, start_time, end_time):
        """Extrai segmento do vídeo."""
        duration = end_time - start_time
        
        cmd = [
            'ffmpeg',
            '-i', input_video,
            '-ss', str(start_time),
            '-t', str(duration),
            '-c', 'copy',
            '-y',
            output_file
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python run_pipeline_FINAL.py <video.mp4> [max_shorts]")
        print("\nExemplo:")
        print("  python run_pipeline_FINAL.py input/live.mp4 10")
        sys.exit(1)
    
    input_video = sys.argv[1]
    max_shorts = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    if not os.path.exists(input_video):
        print(f"❌ Vídeo não encontrado: {input_video}")
        sys.exit(1)
    
    try:
        pipeline = PipelineFinal(input_video, max_shorts)
        pipeline.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário!")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
