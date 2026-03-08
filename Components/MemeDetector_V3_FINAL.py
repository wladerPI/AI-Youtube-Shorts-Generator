# Components/MemeDetector.py
"""
=============================================================================
DETECTOR DE MEMES V3 FINAL - SEM OCR, APENAS VISUAL
=============================================================================

🎯 ABORDAGEM FINAL (HÍBRIDA):
- 80% dos cortes: ÁUDIO ([RISO] + transcrição) - JÁ FUNCIONA
- 20% dos cortes: VISUAL (este arquivo) - Complementar

📊 O QUE FAZ:
1. Detecta GRANDES mudanças visuais nos cantos (memes aparecendo)
2. Salva SCREENSHOT do meme
3. Registra timestamp + posição
4. VOCÊ revisa depois e confirma quais são memes reais

⚠️ SEM OCR:
- OCR estava gerando 99% de lixo (HUD do jogo)
- Melhor salvar imagem e você ver visualmente
- Mais rápido, mais preciso, mais confiável

🎮 OTIMIZADO PARA GAMEPLAY:
- Ignora pequenas mudanças (HUD/animações)
- Detecta apenas aparições súbitas (memes)
- Threshold alto (70% de mudança)

=============================================================================
"""

import cv2
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime


class MemeDetector:
    """
    Detector visual de memes V3 - SEM OCR, com screenshots.
    
    FOCO: Detectar QUANDO meme aparece, não O QUE está escrito.
    """
    
    def __init__(self, video_path, corner_size=0.25):
        """
        Inicializa detector V3.
        
        Args:
            video_path: Caminho do vídeo
            corner_size: Tamanho dos cantos (0.25 = 25%)
        """
        self.video_path = video_path
        self.corner_size = corner_size
        self.meme_events = []
        
        self.cap = cv2.VideoCapture(video_path)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        self._define_regions()
        
        # Criar pasta para screenshots
        self.screenshot_dir = Path("meme_screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def _define_regions(self):
        """Define regiões dos cantos."""
        corner_w = int(self.width * self.corner_size)
        corner_h = int(self.height * self.corner_size)
        
        self.regions = {
            'center': (corner_w, corner_h, self.width - corner_w, self.height - corner_h),
            'top_left': (0, 0, corner_w, corner_h),
            'top_right': (self.width - corner_w, 0, self.width, corner_h),
            'bottom_left': (0, self.height - corner_h, corner_w, self.height),
            'bottom_right': (self.width - corner_w, self.height - corner_h, self.width, self.height)
        }
    
    def detect_memes(self, sample_interval=3.0, change_threshold=0.70):
        """
        Detecta memes visualmente (SEM OCR).
        
        Args:
            sample_interval: Intervalo entre frames (3s = mais rápido)
            change_threshold: Threshold de mudança (0.70 = muito alto)
        
        PARÂMETROS FINAIS OTIMIZADOS:
        - sample_interval=3.0 (analisa 1 frame a cada 3 segundos)
        - change_threshold=0.70 (70% de mudança = apenas memes grandes)
        
        RESULTADO ESPERADO:
        - 30-100 eventos por live de 5h
        - Cada evento tem screenshot salvo
        """
        print(f"🎭 Detectando memes V3 (SEM OCR) em {self.video_path}...")
        print(f"   Dimensões: {self.width}x{self.height}")
        print(f"   FPS: {self.fps:.1f}")
        print(f"   ⚙️ Modo: Visual apenas (screenshots serão salvos)")
        print(f"   ⚙️ Threshold: {change_threshold} (muito alta)")
        
        frame_interval = int(self.fps * sample_interval)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        previous_corners = {corner: None for corner in ['top_left', 'top_right', 'bottom_left', 'bottom_right']}
        active_memes = {}
        
        frame_num = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            if frame_num % frame_interval != 0:
                frame_num += 1
                continue
            
            timestamp = frame_num / self.fps
            
            # Progresso a cada 60s
            if frame_num % (frame_interval * 20) == 0:
                progress = (frame_num / total_frames) * 100
                print(f"   Progresso: {progress:.1f}% - {len(self.meme_events)} memes detectados")
            
            # Verificar cada canto
            for corner_name in ['top_left', 'top_right', 'bottom_left', 'bottom_right']:
                x1, y1, x2, y2 = self.regions[corner_name]
                corner_region = frame[y1:y2, x1:x2]
                
                # Calcular mudança visual
                change_pct = self._calculate_visual_change(corner_region, previous_corners[corner_name])
                
                # FILTRO ÚNICO: Mudança >= 70%
                if change_pct < change_threshold:
                    previous_corners[corner_name] = corner_region.copy()
                    continue
                
                # MUDANÇA GRANDE DETECTADA!
                if corner_name not in active_memes:
                    # MEME APARECEU
                    meme_event = self._process_new_meme(
                        frame, corner_region, corner_name, timestamp
                    )
                    if meme_event:
                        self.meme_events.append(meme_event)
                        active_memes[corner_name] = {
                            'start': timestamp,
                            'meme_id': meme_event['meme_id']
                        }
                        print(f"   🎭 Meme visual detectado em {timestamp:.1f}s ({corner_name})")
                else:
                    # MEME SUMIU
                    meme_data = active_memes.pop(corner_name)
                    duration = timestamp - meme_data['start']
                    
                    # Atualizar duração
                    for event in reversed(self.meme_events):
                        if event['meme_id'] == meme_data['meme_id'] and event['timestamp'] == meme_data['start']:
                            event['duration'] = duration
                            break
                
                previous_corners[corner_name] = corner_region.copy()
            
            frame_num += 1
        
        self.cap.release()
        print(f"✅ Detecção completa: {len(self.meme_events)} eventos visuais")
        print(f"📸 Screenshots salvos em: {self.screenshot_dir}/")
        return self.meme_events
    
    def _calculate_visual_change(self, current_region, previous_region):
        """
        Calcula porcentagem de mudança visual.
        
        ALGORITMO SIMPLES E RÁPIDO:
        - Diferença absoluta de pixels
        - Threshold para binarizar
        - Conta pixels que mudaram
        
        Returns:
            float de 0.0 (igual) a 1.0 (totalmente diferente)
        """
        if previous_region is None:
            return 0.0
        
        # Grayscale
        gray_current = cv2.cvtColor(current_region, cv2.COLOR_BGR2GRAY)
        gray_previous = cv2.cvtColor(previous_region, cv2.COLOR_BGR2GRAY)
        
        # Diferença
        diff = cv2.absdiff(gray_current, gray_previous)
        
        # Binarizar (threshold 40 = ignora mudanças muito sutis)
        _, thresh = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)
        
        # Porcentagem
        change_percentage = np.count_nonzero(thresh) / thresh.size
        
        return change_percentage
    
    def _process_new_meme(self, full_frame, corner_region, position, timestamp):
        """
        Processa novo meme detectado.
        
        O QUE FAZ:
        1. Gera ID único
        2. Salva SCREENSHOT do frame completo
        3. Salva RECORTE do canto onde meme apareceu
        4. Registra evento
        
        SEM OCR - Você revisa visualmente depois!
        """
        # Gerar ID único
        meme_id = f"visual_{int(timestamp)}_{position}"
        
        # Salvar SCREENSHOT DO FRAME COMPLETO
        screenshot_path = self.screenshot_dir / f"{meme_id}_full.jpg"
        cv2.imwrite(str(screenshot_path), full_frame)
        
        # Salvar RECORTE DO CANTO
        corner_path = self.screenshot_dir / f"{meme_id}_corner.jpg"
        cv2.imwrite(str(corner_path), corner_region)
        
        return {
            'timestamp': timestamp,
            'position': position,
            'meme_id': meme_id,
            'duration': 0.0,
            'screenshot_full': str(screenshot_path),
            'screenshot_corner': str(corner_path),
            'type': 'visual_detection',
            'needs_review': True  # Indica que precisa de revisão manual
        }
    
    def save_events(self, session_id):
        """
        Salva eventos em JSON.
        
        FORMATO:
        {
          "total_memes": 45,
          "meme_events": [
            {
              "timestamp": 125.5,
              "position": "top_right",
              "meme_id": "visual_125_top_right",
              "screenshot_full": "meme_screenshots/visual_125_top_right_full.jpg",
              "screenshot_corner": "meme_screenshots/visual_125_top_right_corner.jpg",
              "needs_review": true
            }
          ]
        }
        """
        output_file = f"meme_events_{session_id}.json"
        
        data = {
            'video_path': self.video_path,
            'total_memes': len(self.meme_events),
            'video_dimensions': {
                'width': self.width,
                'height': self.height
            },
            'detection_method': 'visual_only_v3',
            'meme_events': self.meme_events,
            'instructions': 'Revise os screenshots em meme_screenshots/ para confirmar quais são memes reais'
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Eventos salvos em {output_file}")
        return output_file


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def detect_memes_in_video(video_path, session_id, sample_interval=3.0, corner_size=0.25):
    """
    Detecta memes visualmente (SEM OCR).
    
    PARÂMETROS OTIMIZADOS:
    - sample_interval=3.0 (1 frame a cada 3s = rápido)
    - corner_size=0.25 (cantos 25%)
    - change_threshold=0.70 (interno, muito alto)
    
    RESULTADO:
    - JSON com timestamps
    - Screenshots em meme_screenshots/
    - Você revisa visualmente
    """
    detector = MemeDetector(video_path, corner_size=corner_size)
    meme_events = detector.detect_memes(
        sample_interval=sample_interval,
        change_threshold=0.70  # Muito alta
    )
    detector.save_events(session_id)
    return meme_events


# =============================================================================
# SCRIPT DE TESTE
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = "input/live_cortado.mp4"
    
    print("=" * 70)
    print("TESTE DO MEME DETECTOR V3 FINAL (SEM OCR)")
    print("=" * 70)
    
    meme_events = detect_memes_in_video(
        video_path=video_path,
        session_id="test",
        sample_interval=3.0
    )
    
    print("\n📊 RESUMO:")
    print(f"   Total de eventos visuais: {len(meme_events)}")
    print(f"   📸 Screenshots salvos em: meme_screenshots/")
    
    if meme_events:
        print("\n🎭 PRIMEIROS 10 EVENTOS:")
        for event in meme_events[:10]:
            print(f"   {event['timestamp']:.1f}s - {event['position']}")
            print(f"      Ver: {event['screenshot_corner']}")
    
    print("\n✅ Teste completo!")
    print(f"   Resultados: meme_events_test.json")
    print(f"\n📋 PRÓXIMO PASSO:")
    print(f"   1. Abra a pasta meme_screenshots/")
    print(f"   2. Revise as imagens visualmente")
    print(f"   3. Identifique quais são memes reais")
    print(f"   4. Use essas informações no pipeline")


"""
=============================================================================
FILOSOFIA DA V3
=============================================================================

ANTES (V1/V2):
- Tentava fazer OCR do texto dos memes
- OCR gerava 99% de lixo (HUD do jogo)
- Resultado: 1300 "memes" falsos

AGORA (V3):
- Detecta APENAS visualmente (sem OCR)
- Salva screenshot para você ver
- Você decide se é meme real ou não
- Mais rápido, mais preciso, mais confiável

INTEGRAÇÃO COM O PIPELINE:
1. MemeDetector detecta mudanças visuais (este arquivo)
2. Transcription detecta [RISO] no áudio
3. LanguageTasks (GPT) analisa transcrição
4. ProfileManager aprende suas preferências
5. VOCÊ revisa e aprova/rejeita

RESULTADO FINAL:
- 60 momentos do áudio ([RISO] + frases)
- 40 momentos visuais (você confirma)
- 100 clips totais → Você aprova 60 → 60 shorts finais

AJUSTES FINAIS:
Se detectar muito: aumentar change_threshold para 0.80
Se detectar pouco: diminuir para 0.60
Se muito lento: aumentar sample_interval para 5.0

=============================================================================
"""
