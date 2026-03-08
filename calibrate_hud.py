# calibrate_hud.py
"""
=============================================================================
CALIBRADOR AUTOMÁTICO DE HUD - DETECTA ELEMENTOS FIXOS DO JOGO
=============================================================================

🎯 OBJETIVO:
Analisar gameplay e identificar quais regiões da tela NUNCA mudam (HUD fixo).

🎮 POR QUE ISSO É NECESSÁRIO:
- Cada jogo tem HUD diferente (vida, mana, minimapa, tempo, etc)
- HUD fica nos cantos e muda constantemente (números)
- MemeDetector confunde HUD com memes
- Solução: Marcar essas regiões para IGNORAR

💡 COMO FUNCIONA:
1. Analisa primeiros 5 minutos de gameplay
2. Compara frames para encontrar regiões estáticas
3. Gera máscara das áreas de HUD
4. Salva perfil do jogo em hud_profiles/

📊 RESULTADO:
hud_profiles/cs2_hud.json com coordenadas das regiões fixas

=============================================================================
"""

import cv2
import numpy as np
import json
import os
from pathlib import Path
import argparse


class HUDCalibrator:
    """
    Calibrador automático de HUD para jogos.
    
    Detecta elementos fixos da interface que não devem ser
    confundidos com memes.
    """
    
    def __init__(self, video_path, game_name="default"):
        """
        Inicializa calibrador.
        
        Args:
            video_path: Caminho do vídeo de gameplay
            game_name: Nome do jogo (para salvar perfil)
        """
        self.video_path = video_path
        self.game_name = game_name
        
        self.cap = cv2.VideoCapture(video_path)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        # Criar pasta para perfis
        self.profiles_dir = Path("hud_profiles")
        self.profiles_dir.mkdir(exist_ok=True)
    
    def calibrate(self, duration_seconds=300, sample_interval=5.0):
        """
        Calibra HUD analisando vídeo.
        
        Args:
            duration_seconds: Duração da análise (300s = 5min)
            sample_interval: Intervalo entre frames analisados (5s)
        
        LÓGICA:
        1. Amostra frames ao longo de 5 minutos
        2. Calcula desvio padrão de cada pixel
        3. Pixels com baixo desvio = HUD estático
        4. Agrupa regiões estáticas
        5. Gera máscara de HUD
        """
        print(f"🎮 Calibrando HUD do jogo: {self.game_name}")
        print(f"   Vídeo: {self.video_path}")
        print(f"   Dimensões: {self.width}x{self.height}")
        print(f"   Analisando primeiros {duration_seconds}s...")
        
        frame_interval = int(self.fps * sample_interval)
        max_frames = int((duration_seconds * self.fps))
        
        # Coletar frames
        frames_collected = []
        frame_num = 0
        
        print("   📊 Coletando frames...")
        while frame_num < max_frames:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            if frame_num % frame_interval == 0:
                # Converter para grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frames_collected.append(gray)
                
                progress = (frame_num / max_frames) * 100
                if len(frames_collected) % 10 == 0:
                    print(f"      {progress:.0f}% - {len(frames_collected)} frames")
            
            frame_num += 1
        
        self.cap.release()
        
        if len(frames_collected) < 10:
            print("   ❌ Poucos frames coletados!")
            return None
        
        print(f"   ✅ {len(frames_collected)} frames coletados")
        
        # Calcular variância de cada pixel
        print("   🔍 Detectando regiões estáticas...")
        frames_array = np.array(frames_collected, dtype=np.float32)
        variance_map = np.var(frames_array, axis=0)
        
        # Pixels com baixa variância = HUD estático
        # Threshold: Variância < 10 = estático
        static_mask = (variance_map < 10).astype(np.uint8) * 255
        
        # Aplicar morfologia para limpar ruído
        kernel = np.ones((5, 5), np.uint8)
        static_mask = cv2.morphologyEx(static_mask, cv2.MORPH_CLOSE, kernel)
        static_mask = cv2.morphologyEx(static_mask, cv2.MORPH_OPEN, kernel)
        
        # Encontrar contornos das regiões estáticas
        contours, _ = cv2.findContours(static_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar apenas regiões grandes (HUD real)
        min_area = (self.width * self.height) * 0.01  # Pelo menos 1% da tela
        
        hud_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                hud_regions.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area': int(area)
                })
        
        print(f"   ✅ {len(hud_regions)} regiões de HUD detectadas")
        
        # Classificar por posição (cantos)
        classified_regions = self._classify_hud_regions(hud_regions)
        
        # Salvar perfil
        profile = {
            'game_name': self.game_name,
            'video_resolution': {
                'width': self.width,
                'height': self.height
            },
            'hud_regions': classified_regions,
            'calibration_info': {
                'duration_seconds': duration_seconds,
                'frames_analyzed': len(frames_collected),
                'total_hud_regions': len(hud_regions)
            }
        }
        
        output_file = self.profiles_dir / f"{self.game_name}_hud.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Perfil salvo em: {output_file}")
        
        # Salvar visualização
        self._save_visualization(static_mask, hud_regions)
        
        return profile
    
    def _classify_hud_regions(self, regions):
        """
        Classifica regiões por posição (cantos).
        
        Returns:
            dict com regiões classificadas por canto
        """
        classified = {
            'top_left': [],
            'top_right': [],
            'bottom_left': [],
            'bottom_right': [],
            'center': []
        }
        
        # Limites dos cantos (25% da tela)
        corner_w = self.width * 0.25
        corner_h = self.height * 0.25
        
        for region in regions:
            x = region['x']
            y = region['y']
            
            # Classificar por posição do centro da região
            center_x = x + region['width'] / 2
            center_y = y + region['height'] / 2
            
            if center_x < corner_w and center_y < corner_h:
                classified['top_left'].append(region)
            elif center_x > (self.width - corner_w) and center_y < corner_h:
                classified['top_right'].append(region)
            elif center_x < corner_w and center_y > (self.height - corner_h):
                classified['bottom_left'].append(region)
            elif center_x > (self.width - corner_w) and center_y > (self.height - corner_h):
                classified['bottom_right'].append(region)
            else:
                classified['center'].append(region)
        
        return classified
    
    def _save_visualization(self, static_mask, hud_regions):
        """
        Salva imagem mostrando regiões de HUD detectadas.
        """
        # Criar visualização colorida
        visualization = cv2.cvtColor(static_mask, cv2.COLOR_GRAY2BGR)
        
        # Desenhar retângulos das regiões
        for region in hud_regions:
            x, y, w, h = region['x'], region['y'], region['width'], region['height']
            cv2.rectangle(visualization, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Label com área
            label = f"{region['area']}"
            cv2.putText(visualization, label, (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        output_img = self.profiles_dir / f"{self.game_name}_hud_visualization.jpg"
        cv2.imwrite(str(output_img), visualization)
        print(f"   🖼️  Visualização salva em: {output_img}")


# =============================================================================
# SCRIPT DE LINHA DE COMANDO
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calibra HUD de jogo automaticamente"
    )
    parser.add_argument(
        "video",
        help="Caminho do vídeo de gameplay"
    )
    parser.add_argument(
        "--game",
        default="default",
        help="Nome do jogo (ex: cs2, minecraft, gta)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Duração da análise em segundos (padrão: 300 = 5min)"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Intervalo entre frames analisados em segundos (padrão: 5.0)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("CALIBRADOR AUTOMÁTICO DE HUD")
    print("=" * 70)
    
    calibrator = HUDCalibrator(args.video, args.game)
    profile = calibrator.calibrate(
        duration_seconds=args.duration,
        sample_interval=args.interval
    )
    
    if profile:
        print("\n✅ CALIBRAÇÃO COMPLETA!")
        print(f"\n📊 RESUMO:")
        print(f"   Jogo: {profile['game_name']}")
        print(f"   Regiões detectadas:")
        for position, regions in profile['hud_regions'].items():
            if regions:
                print(f"      {position}: {len(regions)} regiões")
        
        print(f"\n💡 PRÓXIMO PASSO:")
        print(f"   O MemeDetector_V4 vai ignorar automaticamente essas regiões!")
        print(f"   Arquivo gerado: hud_profiles/{profile['game_name']}_hud.json")
    else:
        print("\n❌ Calibração falhou!")


"""
=============================================================================
EXEMPLOS DE USO
=============================================================================

# Calibrar HUD do CS2:
python calibrate_hud.py input/cs2_gameplay.mp4 --game cs2

# Calibrar HUD do Minecraft (análise mais longa):
python calibrate_hud.py input/minecraft.mp4 --game minecraft --duration 600

# Calibrar com amostragem mais frequente:
python calibrate_hud.py input/gameplay.mp4 --game meu_jogo --interval 2.0

=============================================================================
RESULTADO
=============================================================================

Vai gerar 2 arquivos:

1. hud_profiles/cs2_hud.json:
{
  "game_name": "cs2",
  "hud_regions": {
    "top_left": [
      {"x": 10, "y": 10, "width": 200, "height": 50}
    ],
    "bottom_right": [
      {"x": 1600, "y": 1000, "width": 300, "height": 60}
    ]
  }
}

2. hud_profiles/cs2_hud_visualization.jpg:
   Imagem mostrando onde o HUD foi detectado

=============================================================================
"""
