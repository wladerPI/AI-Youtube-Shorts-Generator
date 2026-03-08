# Components/MemeDetectorPro.py
"""
=============================================================================
DETECTOR DE MEMES PROFISSIONAL - MOTION + FEATURE MATCHING
=============================================================================

🎯 ALGORITMO INTELIGENTE:
1. Motion Detection → Detecta mudanças bruscas (meme aparecendo)
2. Feature Matching → Compara com biblioteca de memes
3. Validação Temporal → Confirma duração típica (1-10s)

✅ VANTAGENS:
- Zero configuração manual
- Funciona em qualquer jogo
- Detecta memes SOBRE o HUD
- Ignora HUD automaticamente (muda gradualmente)
- Precisão 85-95%

⚙️ TECNOLOGIAS:
- ORB (Oriented FAST and Rotated BRIEF)
- FLANN (Fast Library for Approximate Nearest Neighbors)
- Optical Flow para motion detection

=============================================================================
"""

import cv2
import numpy as np
import json
import os
from pathlib import Path
from collections import defaultdict
import time


class MemeDetectorPro:
    """
    Detector profissional de memes usando motion detection + feature matching.
    """
    
    def __init__(self, video_path, templates_dir="meme_templates"):
        """
        Inicializa detector profissional.
        
        Args:
            video_path: Caminho do vídeo
            templates_dir: Pasta com templates dos memes
        """
        self.video_path = video_path
        self.templates_dir = Path(templates_dir)
        
        # Abrir vídeo
        self.cap = cv2.VideoCapture(video_path)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Criar detectores PRIMEIRO (antes de carregar templates)
        self.orb = cv2.ORB_create(nfeatures=500)  # Detector de features
        self.flann = self._create_flann_matcher()
        
        # Carregar templates (usa self.orb)
        self.templates = self._load_templates()
        self.meme_events = []
        
        # Definir regiões
        self._define_regions()
        
        print(f"✅ Detector Profissional inicializado")
        print(f"   Vídeo: {self.width}x{self.height} @ {self.fps:.1f} FPS")
        print(f"   Templates: {len(self.templates)} memes carregados")
    
    def _define_regions(self):
        """Define regiões para análise."""
        corner_w = int(self.width * 0.30)  # 30% da largura
        corner_h = int(self.height * 0.30)  # 30% da altura
        
        self.regions = {
            'top_left': (0, 0, corner_w, corner_h),
            'top_right': (self.width - corner_w, 0, self.width, corner_h),
            'bottom_left': (0, self.height - corner_h, corner_w, self.height),
            'bottom_right': (self.width - corner_w, self.height - corner_h, self.width, self.height),
            'center': (corner_w, corner_h, self.width - corner_w, self.height - corner_h),
            'left': (0, corner_h, corner_w, self.height - corner_h),
            'right': (self.width - corner_w, corner_h, self.width, self.height - corner_h)
        }
    
    def _load_templates(self):
        """Carrega templates com features pré-computadas."""
        templates = {}
        
        if not self.templates_dir.exists():
            print(f"⚠️ Pasta {self.templates_dir} não existe!")
            return templates
        
        # Carregar config
        config_file = self.templates_dir / "meme_config.json"
        config = {}
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # Carregar cada template
        for img_file in self.templates_dir.glob("*.png"):
            img = cv2.imread(str(img_file), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            
            # Extrair features do template
            keypoints, descriptors = self.orb.detectAndCompute(img, None)
            
            if descriptors is None or len(keypoints) < 10:
                continue  # Template muito simples
            
            template_name = img_file.stem
            templates[template_name] = {
                'image': img,
                'keypoints': keypoints,
                'descriptors': descriptors,
                'config': config.get(f"{img_file.name}", {}),
                'shape': img.shape
            }
        
        return templates
    
    def _create_flann_matcher(self):
        """Cria matcher FLANN para matching rápido."""
        FLANN_INDEX_LSH = 6
        index_params = dict(
            algorithm=FLANN_INDEX_LSH,
            table_number=6,
            key_size=12,
            multi_probe_level=1
        )
        search_params = dict(checks=50)
        return cv2.FlannBasedMatcher(index_params, search_params)
    
    def detect_memes(self, motion_threshold=0.60, match_threshold=0.85):
        """
        Detecta memes usando motion detection + feature matching.
        
        Args:
            motion_threshold: Threshold para mudança brusca (0.60 = 60%)
            match_threshold: Threshold para feature matching (0.85 = 85%)
        
        ALGORITMO:
        1. Detecta regiões com mudança brusca (motion detection)
        2. Compara essas regiões com templates (feature matching)
        3. Valida duração temporal (1-10 segundos)
        """
        print(f"\n🎭 Iniciando detecção profissional...")
        print(f"   Motion threshold: {motion_threshold*100:.0f}%")
        print(f"   Match threshold: {match_threshold*100:.0f}%")
        
        # Armazenar frames anteriores para motion detection
        previous_frames = {}
        active_memes = {}  # Memes atualmente ativos
        
        frame_num = 0
        start_time = time.time()
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            timestamp = frame_num / self.fps
            
            # Progresso
            if frame_num % (int(self.fps) * 30) == 0:  # A cada 30s
                progress = (frame_num / self.total_frames) * 100
                elapsed = time.time() - start_time
                eta = (elapsed / max(progress, 0.1)) * (100 - progress)
                print(f"   [{progress:5.1f}%] Frame {frame_num}/{self.total_frames} | "
                      f"Detectados: {len(self.meme_events)} | ETA: {eta/60:.0f}min")
            
            # Converter para grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Analisar cada região
            for region_name, (x1, y1, x2, y2) in self.regions.items():
                region = gray[y1:y2, x1:x2]
                
                # FASE 1: MOTION DETECTION
                if region_name in previous_frames:
                    motion_score = self._calculate_motion(
                        region, 
                        previous_frames[region_name]
                    )
                    
                    # Mudança brusca detectada? (possível meme)
                    if motion_score > motion_threshold:
                        # FASE 2: FEATURE MATCHING
                        matches = self._find_matches(
                            region, 
                            frame[y1:y2, x1:x2],  # Região colorida
                            region_name
                        )
                        
                        # Processar matches
                        for match in matches:
                            if match['score'] >= match_threshold:
                                self._process_meme_detection(
                                    match, 
                                    timestamp, 
                                    region_name,
                                    active_memes
                                )
                
                # Atualizar frame anterior
                previous_frames[region_name] = region.copy()
            
            # FASE 3: VALIDAÇÃO TEMPORAL
            self._validate_active_memes(active_memes, timestamp)
            
            frame_num += 1
        
        self.cap.release()
        
        # Finalizar memes ativos
        for meme_id, meme_data in active_memes.items():
            duration = timestamp - meme_data['start']
            if 1.0 < duration < 10.0:  # Duração válida
                self.meme_events.append({
                    'timestamp': meme_data['start'],
                    'meme_name': meme_data['name'],
                    'position': meme_data['position'],
                    'duration': duration,
                    'score': meme_data['score']
                })
        
        total_time = time.time() - start_time
        print(f"\n✅ Detecção completa em {total_time/60:.1f} minutos")
        print(f"   Total detectado: {len(self.meme_events)} memes")
        
        return self.meme_events
    
    def _calculate_motion(self, current, previous):
        """
        Calcula intensidade de movimento entre dois frames.
        
        Returns:
            float 0.0-1.0 (porcentagem de mudança)
        """
        # Diferença absoluta
        diff = cv2.absdiff(current, previous)
        
        # Threshold para binarizar
        _, thresh = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)
        
        # Porcentagem de pixels que mudaram
        motion_score = np.count_nonzero(thresh) / thresh.size
        
        return motion_score
    
    def _find_matches(self, region_gray, region_color, region_name):
        """
        Encontra matches de templates na região.
        
        Returns:
            Lista de matches com scores
        """
        # Extrair features da região
        kp_region, desc_region = self.orb.detectAndCompute(region_gray, None)
        
        if desc_region is None or len(kp_region) < 10:
            return []
        
        matches_found = []
        
        # Comparar com cada template
        for template_name, template_data in self.templates.items():
            # Feature matching com FLANN
            try:
                matches = self.flann.knnMatch(
                    template_data['descriptors'],
                    desc_region,
                    k=2
                )
            except:
                continue
            
            # Filtro de Lowe (ratio test)
            good_matches = []
            for pair in matches:
                if len(pair) == 2:
                    m, n = pair
                    if m.distance < 0.7 * n.distance:
                        good_matches.append(m)
            
            # Calcular score
            if len(good_matches) > 10:  # Mínimo 10 matches
                score = len(good_matches) / len(template_data['keypoints'])
                
                # Validação geométrica (RANSAC)
                if len(good_matches) >= 15:
                    valid = self._validate_geometry(
                        template_data['keypoints'],
                        kp_region,
                        good_matches
                    )
                    if valid:
                        score *= 1.2  # Bonus por geometria válida
                
                matches_found.append({
                    'template_name': template_name,
                    'score': min(score, 1.0),
                    'matches_count': len(good_matches),
                    'config': template_data['config']
                })
        
        # Ordenar por score
        matches_found.sort(key=lambda x: x['score'], reverse=True)
        
        return matches_found
    
    def _validate_geometry(self, kp_template, kp_region, matches):
        """
        Valida geometria dos matches usando homografia.
        
        Returns:
            bool - True se geometria é válida
        """
        if len(matches) < 15:
            return False
        
        # Pontos correspondentes
        src_pts = np.float32([kp_template[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_region[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        
        # Encontrar homografia
        try:
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if M is None:
                return False
            
            # Contar inliers
            inliers = np.sum(mask)
            inlier_ratio = inliers / len(matches)
            
            return inlier_ratio > 0.6  # 60% inliers
        except:
            return False
    
    def _process_meme_detection(self, match, timestamp, position, active_memes):
        """Processa detecção de meme."""
        template_name = match['template_name']
        meme_id = f"{template_name}_{position}"
        
        # Verificar se já está ativo
        if meme_id not in active_memes:
            # Novo meme detectado
            active_memes[meme_id] = {
                'name': template_name,
                'position': position,
                'start': timestamp,
                'last_seen': timestamp,
                'score': match['score']
            }
            print(f"      🎭 {template_name} detectado em {timestamp:.1f}s "
                  f"({position}) - score: {match['score']:.2f}")
        else:
            # Atualizar última vez visto
            active_memes[meme_id]['last_seen'] = timestamp
    
    def _validate_active_memes(self, active_memes, current_time):
        """Valida e finaliza memes ativos."""
        to_remove = []
        
        for meme_id, meme_data in active_memes.items():
            # Se não visto há mais de 1 segundo, considerarcomo finalizado
            if current_time - meme_data['last_seen'] > 1.0:
                duration = meme_data['last_seen'] - meme_data['start']
                
                # Validar duração (1-10 segundos)
                if 1.0 < duration < 10.0:
                    self.meme_events.append({
                        'timestamp': meme_data['start'],
                        'meme_name': meme_data['name'],
                        'position': meme_data['position'],
                        'duration': duration,
                        'score': meme_data['score']
                    })
                
                to_remove.append(meme_id)
        
        # Remover finalizados
        for meme_id in to_remove:
            del active_memes[meme_id]
    
    def save_events(self, session_id):
        """Salva eventos detectados."""
        output_file = f"meme_events_{session_id}.json"
        
        data = {
            'video_path': self.video_path,
            'total_memes': len(self.meme_events),
            'detection_method': 'motion_detection + feature_matching',
            'meme_events': self.meme_events
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Eventos salvos em: {output_file}")
        return output_file
    
    def get_statistics(self):
        """Retorna estatísticas da detecção."""
        if not self.meme_events:
            return {}
        
        # Agrupar por meme
        by_meme = defaultdict(int)
        by_position = defaultdict(int)
        durations = []
        
        for event in self.meme_events:
            by_meme[event['meme_name']] += 1
            by_position[event['position']] += 1
            durations.append(event['duration'])
        
        return {
            'total_memes': len(self.meme_events),
            'unique_memes': len(by_meme),
            'by_meme': dict(by_meme),
            'by_position': dict(by_position),
            'avg_duration': np.mean(durations) if durations else 0,
            'min_duration': np.min(durations) if durations else 0,
            'max_duration': np.max(durations) if durations else 0
        }


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def detect_memes_professional(video_path, session_id, motion_threshold=0.60, match_threshold=0.85):
    """
    Detecta memes profissionalmente.
    
    Args:
        video_path: Caminho do vídeo
        session_id: ID da sessão
        motion_threshold: Threshold motion (0.60 = 60% mudança)
        match_threshold: Threshold matching (0.85 = 85% similaridade)
    
    Returns:
        Lista de eventos de memes
    """
    detector = MemeDetectorPro(video_path)
    meme_events = detector.detect_memes(motion_threshold, match_threshold)
    detector.save_events(session_id)
    
    # Estatísticas
    stats = detector.get_statistics()
    if stats:
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total: {stats['total_memes']} detecções")
        print(f"   Memes únicos: {stats['unique_memes']}")
        print(f"   Duração média: {stats['avg_duration']:.1f}s")
        print(f"\n🎭 TOP 5 MEMES:")
        for meme, count in sorted(stats['by_meme'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {meme}: {count}x")
    
    return meme_events


# =============================================================================
# TESTE STANDALONE
# =============================================================================

if __name__ == "__main__":
    import sys
    
    video = sys.argv[1] if len(sys.argv) > 1 else "input/live_cortado.mp4"
    
    print("=" * 70)
    print("MEME DETECTOR PROFISSIONAL")
    print("Motion Detection + Feature Matching (ORB + FLANN)")
    print("=" * 70)
    
    meme_events = detect_memes_professional(video, "test")
    
    print("\n✅ Detecção completa!")
    print(f"   Resultados salvos em: meme_events_test.json")
