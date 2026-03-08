# Components/MemeDetector.py - V4 TEMPLATE MATCHING
"""
DETECTOR DE MEMES V4 - TEMPLATE MATCHING
Reconhece memes cadastrados em meme_templates/
Ignora HUD baseado em hud_profiles/
"""

import cv2
import numpy as np
import json
import os
from pathlib import Path

class MemeDetector:
    def __init__(self, video_path, game_name="default"):
        self.video_path = video_path
        self.game_name = game_name
        self.meme_events = []
        
        self.cap = cv2.VideoCapture(video_path)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        # Carregar templates e HUD
        self.templates = self._load_templates()
        self.hud_mask = self._load_hud_profile()
        
        Path("meme_screenshots").mkdir(exist_ok=True)
    
    def _load_templates(self):
        """Carrega templates de meme_templates/"""
        templates = {}
        templates_dir = Path("meme_templates")
        
        if not templates_dir.exists():
            print(f"⚠️ Pasta meme_templates/ não existe. Criando...")
            templates_dir.mkdir()
            return templates
        
        # Carregar config
        config_file = templates_dir / "meme_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Carregar imagens
        for img_file in templates_dir.glob("*.png"):
            template_img = cv2.imread(str(img_file))
            if template_img is not None:
                template_name = img_file.stem
                templates[template_name] = {
                    'image': template_img,
                    'config': config.get(f"{img_file.name}", {})
                }
        
        print(f"✅ {len(templates)} templates carregados")
        return templates
    
    def _load_hud_profile(self):
        """Carrega perfil de HUD para ignorar regiões"""
        profile_file = Path("hud_profiles") / f"{self.game_name}_hud.json"
        
        if not profile_file.exists():
            print(f"⚠️ Perfil de HUD não encontrado: {profile_file}")
            print(f"   Execute: python calibrate_hud.py input/video.mp4 --game {self.game_name}")
            return None
        
        with open(profile_file, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        # Criar máscara de HUD (0 = ignorar, 255 = processar)
        mask = np.ones((self.height, self.width), dtype=np.uint8) * 255
        
        for position, regions in profile['hud_regions'].items():
            for region in regions:
                x, y, w, h = region['x'], region['y'], region['width'], region['height']
                # Marcar região como ignorada
                mask[y:y+h, x:x+w] = 0
        
        print(f"✅ Perfil de HUD carregado: {len(profile['hud_regions'])} regiões ignoradas")
        return mask
    
    def detect_memes(self, sample_interval=2.0, min_match=0.75):
        """
        Detecta memes usando Template Matching.
        
        Args:
            sample_interval: Intervalo entre frames (2s)
            min_match: Similaridade mínima (0.75 = 75%)
        """
        if not self.templates:
            print("❌ Nenhum template carregado! Adicione imagens em meme_templates/")
            return []
        
        print(f"🎭 Detectando memes V4 (Template Matching)...")
        print(f"   {len(self.templates)} templates carregados")
        
        frame_interval = int(self.fps * sample_interval)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_num = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            if frame_num % frame_interval != 0:
                frame_num += 1
                continue
            
            timestamp = frame_num / self.fps
            
            # Progresso
            if frame_num % (frame_interval * 30) == 0:
                progress = (frame_num / total_frames) * 100
                print(f"   Progresso: {progress:.1f}% - {len(self.meme_events)} memes")
            
            # Aplicar máscara de HUD (se existir)
            if self.hud_mask is not None:
                frame_masked = cv2.bitwise_and(frame, frame, mask=self.hud_mask)
            else:
                frame_masked = frame
            
            # Procurar cada template
            for template_name, template_data in self.templates.items():
                template_img = template_data['image']
                config = template_data['config']
                
                # Template Matching
                result = cv2.matchTemplate(frame_masked, template_img, cv2.TM_CCOEFF_NORMED)
                locations = np.where(result >= min_match)
                
                # Se encontrou match
                for pt in zip(*locations[::-1]):
                    meme_event = {
                        'timestamp': timestamp,
                        'meme_name': template_name,
                        'position': self._classify_position(pt[0], pt[1]),
                        'match_score': float(result[pt[1], pt[0]]),
                        'location': {'x': int(pt[0]), 'y': int(pt[1])},
                        'description': config.get('description', template_name)
                    }
                    
                    # Evitar duplicatas (mesmo meme no mesmo segundo)
                    if not self._is_duplicate(meme_event):
                        self.meme_events.append(meme_event)
                        print(f"   🎭 {template_name} detectado em {timestamp:.1f}s (match: {meme_event['match_score']:.2f})")
                        
                        # Salvar screenshot
                        self._save_screenshot(frame, pt, template_img.shape, template_name, timestamp)
            
            frame_num += 1
        
        self.cap.release()
        print(f"✅ {len(self.meme_events)} memes detectados")
        return self.meme_events
    
    def _classify_position(self, x, y):
        """Classifica posição do meme"""
        corner_w = self.width * 0.25
        corner_h = self.height * 0.25
        
        if x < corner_w and y < corner_h:
            return 'top_left'
        elif x > (self.width - corner_w) and y < corner_h:
            return 'top_right'
        elif x < corner_w and y > (self.height - corner_h):
            return 'bottom_left'
        elif x > (self.width - corner_w) and y > (self.height - corner_h):
            return 'bottom_right'
        else:
            return 'center'
    
    def _is_duplicate(self, new_event):
        """Verifica se já detectou este meme recentemente"""
        for event in self.meme_events[-5:]:  # Últimos 5
            if (event['meme_name'] == new_event['meme_name'] and 
                abs(event['timestamp'] - new_event['timestamp']) < 3.0):
                return True
        return False
    
    def _save_screenshot(self, frame, location, template_shape, meme_name, timestamp):
        """Salva screenshot do meme detectado"""
        x, y = location
        h, w = template_shape[:2]
        
        # Recortar região
        crop = frame[y:y+h, x:x+w]
        
        # Salvar
        filename = f"meme_screenshots/{meme_name}_{int(timestamp)}.jpg"
        cv2.imwrite(filename, crop)
    
    def save_events(self, session_id):
        """Salva eventos em JSON"""
        output_file = f"meme_events_{session_id}.json"
        
        data = {
            'video_path': self.video_path,
            'total_memes': len(self.meme_events),
            'detection_method': 'template_matching_v4',
            'templates_used': list(self.templates.keys()),
            'meme_events': self.meme_events
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Eventos salvos em {output_file}")
        return output_file


def detect_memes_in_video(video_path, session_id, game_name="default", sample_interval=2.0):
    detector = MemeDetector(video_path, game_name=game_name)
    meme_events = detector.detect_memes(sample_interval=sample_interval)
    detector.save_events(session_id)
    return meme_events


if __name__ == "__main__":
    import sys
    
    video = sys.argv[1] if len(sys.argv) > 1 else "input/live_cortado.mp4"
    game = sys.argv[2] if len(sys.argv) > 2 else "default"
    
    print("=" * 70)
    print("MEME DETECTOR V4 - TEMPLATE MATCHING")
    print("=" * 70)
    
    meme_events = detect_memes_in_video(video, "test", game_name=game)
    
    print("\n📊 RESUMO:")
    print(f"   Total: {len(meme_events)} memes detectados")
    
    if meme_events:
        # Agrupar por meme
        by_meme = {}
        for event in meme_events:
            name = event['meme_name']
            by_meme[name] = by_meme.get(name, 0) + 1
        
        print("\n🎭 MEMES DETECTADOS:")
        for meme_name, count in sorted(by_meme.items(), key=lambda x: x[1], reverse=True):
            print(f"   {meme_name}: {count}x")
    
    print("\n✅ Teste completo!")
