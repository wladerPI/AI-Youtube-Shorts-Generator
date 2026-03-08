# Render/CameraControllerV2.py
"""
=============================================================================
CONTROLADOR DE CÂMERA INTELIGENTE V2 - FOCA EM MEMES
=============================================================================

🎯 OBJETIVO:
Movimento de câmera inteligente que FOCA em memes nos cantos da tela.

🎮 COMPORTAMENTO ESPECÍFICO PARA LIVES DO 11CLOSED:
Estado padrão: SEMPRE NO CENTRO (foco no gameplay)
Quando meme aparece: Suavemente move para o canto
Foca no meme por 3-6s
Suavemente volta ao CENTRO

📐 LÓGICA DE MOVIMENTO:
┌────────────────────────────────────────┐
│  ESTADO 1: CENTRO (padrão)             │
│  Câmera focada no gameplay principal   │
└────────────────────────────────────────┘
            ↓ (meme aparece)
┌────────────────────────────────────────┐
│  TRANSIÇÃO (1s)                        │
│  Suavemente move para o canto         │
└────────────────────────────────────────┘
            ↓
┌────────────────────────────────────────┐
│  ESTADO 2: CANTO (3-6s)                │
│  Foca no meme                          │
└────────────────────────────────────────┘
            ↓ (meme some)
┌────────────────────────────────────────┐
│  TRANSIÇÃO (1s)                        │
│  Suavemente volta ao centro            │
└────────────────────────────────────────┘
            ↓
┌────────────────────────────────────────┐
│  ESTADO 1: CENTRO (volta ao padrão)    │
└────────────────────────────────────────┘

⚙️ PARÂMETROS AJUSTÁVEIS:
- transition_speed: Velocidade do movimento (1.0s padrão)
- focus_duration: Tempo focado no meme (3-6s)
- smoothing_factor: Suavidade do movimento (0.8 padrão)
- corner_margin: Margem dos cantos (50px)

🔄 INTEGRAÇÃO:
- Usa meme_events.json do MemeDetector
- Coordena com VerticalCropper
- Sincronizado com legendas

=============================================================================
"""

import numpy as np
from typing import List, Tuple, Dict, Optional


class CameraControllerV2:
    """
    Controlador de câmera inteligente para focar em memes.
    
    DIFERENÇAS DA V1:
    - V1: Movimento aleatório ou baseado em rosto
    - V2: Movimento baseado em EVENTOS DE MEMES detectados
    """
    
    def __init__(
        self,
        video_width: int,
        video_height: int,
        output_width: int,
        output_height: int,
        meme_events: List[Dict],
        fps: float = 30.0
    ):
        """
        Inicializa controlador.
        
        Args:
            video_width: Largura do vídeo original
            video_height: Altura do vídeo original
            output_width: Largura do output vertical (ex: 1080)
            output_height: Altura do output vertical (ex: 1920)
            meme_events: Lista de eventos de memes do MemeDetector
            fps: Frames por segundo do vídeo
        
        EXEMPLO:
        Video original: 1920x1080 (horizontal)
        Output: 1080x1920 (vertical)
        
        Câmera precisa escolher qual parte dos 1920px horizontais vai mostrar.
        """
        self.video_width = video_width
        self.video_height = video_height
        self.output_width = output_width
        self.output_height = output_height
        self.meme_events = meme_events
        self.fps = fps
        
        # Estado atual da câmera
        self.current_x = video_width / 2  # Começa no centro
        self.current_state = "center"  # "center", "transition_to_meme", "focusing_meme", "transition_to_center"
        
        # Parâmetros ajustáveis
        self.transition_speed = 1.0  # segundos para transição
        self.smoothing_factor = 0.8  # 0.0-1.0, maior = mais suave
        self.corner_margin = 50  # pixels de margem dos cantos
        
        # Índice do meme ativo
        self.active_meme_idx = None
        self.meme_focus_start = None
        
        # Posições dos cantos
        self._define_corner_positions()
    
    def _define_corner_positions(self):
        """
        Define posições X dos cantos para focar.
        
        COORDENADAS:
        - top_left / bottom_left: corner_margin (ex: 50px)
        - center: video_width / 2 (ex: 960px)
        - top_right / bottom_right: video_width - corner_margin (ex: 1870px)
        
        NOTA: Posição Y não muda (câmera só move horizontalmente)
        """
        self.corner_positions = {
            'center': self.video_width / 2,
            'top_left': self.corner_margin + (self.output_width / 2),
            'bottom_left': self.corner_margin + (self.output_width / 2),
            'top_right': self.video_width - self.corner_margin - (self.output_width / 2),
            'bottom_right': self.video_width - self.corner_margin - (self.output_width / 2)
        }
    
    def get_camera_position(self, current_time: float) -> Tuple[float, str]:
        """
        Retorna posição X da câmera no tempo atual.
        
        Args:
            current_time: Tempo atual do vídeo em segundos
        
        Returns:
            (x_position, state) onde:
            - x_position: Coordenada X do centro da câmera
            - state: Estado atual ("center", "focusing_meme", etc)
        
        LÓGICA DE ESTADO:
        1. Verificar se há meme ativo neste momento
        2. Se sim e ainda não está focando: iniciar transição
        3. Se está focando: manter foco
        4. Se meme acabou: transição de volta ao centro
        """
        # Verificar se há meme ativo
        active_meme = self._get_active_meme(current_time)
        
        if active_meme:
            # HÁ MEME ATIVO
            target_x = self.corner_positions[active_meme['position']]
            
            if self.current_state == "center":
                # Estava no centro, iniciar transição para meme
                self.current_state = "transition_to_meme"
                self.active_meme_idx = active_meme['index']
                self.meme_focus_start = current_time
            
            elif self.current_state == "transition_to_meme":
                # Em transição, continuar movendo
                if abs(self.current_x - target_x) < 10:  # Chegou perto
                    self.current_state = "focusing_meme"
            
            # Suavizar movimento
            self.current_x = self._smooth_transition(
                self.current_x, 
                target_x,
                speed_factor=1.0
            )
        
        else:
            # SEM MEME ATIVO - VOLTAR AO CENTRO
            center_x = self.corner_positions['center']
            
            if self.current_state in ["focusing_meme", "transition_to_meme"]:
                # Estava focando meme, iniciar volta ao centro
                self.current_state = "transition_to_center"
                self.active_meme_idx = None
            
            elif self.current_state == "transition_to_center":
                # Em transição de volta
                if abs(self.current_x - center_x) < 10:  # Chegou ao centro
                    self.current_state = "center"
            
            # Suavizar movimento de volta
            self.current_x = self._smooth_transition(
                self.current_x,
                center_x,
                speed_factor=0.8  # Volta um pouco mais lento
            )
        
        return self.current_x, self.current_state
    
    def _get_active_meme(self, current_time: float) -> Optional[Dict]:
        """
        Verifica se há meme ativo no tempo atual.
        
        Args:
            current_time: Tempo em segundos
        
        Returns:
            Dict do meme ativo ou None
            {
              'index': 0,
              'timestamp': 125.5,
              'position': 'top_right',
              'duration': 4.2,
              'text': 'KKKK ELE MORREU'
            }
        
        LÓGICA:
        - Meme está ativo se: timestamp <= current_time <= timestamp + duration
        - Se múltiplos memes simultâneos: priorizar por confidence
        """
        active_memes = []
        
        for idx, meme in enumerate(self.meme_events):
            start = meme['timestamp']
            end = start + meme.get('duration', 4.0)
            
            if start <= current_time <= end:
                active_memes.append({
                    'index': idx,
                    **meme
                })
        
        if not active_memes:
            return None
        
        # Se múltiplos, priorizar por confidence
        active_memes.sort(key=lambda m: m.get('confidence', 0.5), reverse=True)
        return active_memes[0]
    
    def _smooth_transition(
        self,
        current_pos: float,
        target_pos: float,
        speed_factor: float = 1.0
    ) -> float:
        """
        Suaviza transição entre posições.
        
        Args:
            current_pos: Posição atual
            target_pos: Posição alvo
            speed_factor: Multiplicador de velocidade (1.0 = normal)
        
        Returns:
            Nova posição suavizada
        
        ALGORITMO:
        Interpolação exponencial (ease-out)
        new_pos = current * smoothing + target * (1 - smoothing)
        
        SMOOTHING_FACTOR:
        - 0.9 = muito suave (lento)
        - 0.8 = suave (padrão)
        - 0.5 = rápido
        - 0.0 = instantâneo
        """
        # Calcular distância
        distance = abs(target_pos - current_pos)
        
        # Se muito longe, aumentar velocidade inicial
        if distance > 500:
            speed_factor *= 1.3
        
        # Interpolação suavizada
        alpha = 1.0 - (self.smoothing_factor / speed_factor)
        new_pos = current_pos * (1 - alpha) + target_pos * alpha
        
        return new_pos
    
    def calculate_crop_box(
        self,
        camera_x: float,
        frame_height: int
    ) -> Tuple[int, int, int, int]:
        """
        Calcula coordenadas da região a ser cortada.
        
        Args:
            camera_x: Posição X do centro da câmera
            frame_height: Altura do frame
        
        Returns:
            (x1, y1, x2, y2) coordenadas do crop
        
        CÁLCULO:
        - x1 = camera_x - (output_width / 2)
        - x2 = camera_x + (output_width / 2)
        - y1 = 0 (começo do frame)
        - y2 = frame_height (fim do frame)
        
        VALIDAÇÃO:
        - Garante que crop não sai dos limites do vídeo
        """
        half_width = self.output_width / 2
        
        x1 = int(camera_x - half_width)
        x2 = int(camera_x + half_width)
        
        # Validar limites
        if x1 < 0:
            x1 = 0
            x2 = self.output_width
        elif x2 > self.video_width:
            x2 = self.video_width
            x1 = self.video_width - self.output_width
        
        y1 = 0
        y2 = frame_height
        
        return x1, y1, x2, y2
    
    def generate_camera_path(self, duration: float) -> List[Tuple[float, float, str]]:
        """
        Gera caminho completo da câmera para todo o vídeo.
        
        Args:
            duration: Duração total do vídeo em segundos
        
        Returns:
            Lista de (time, x_position, state) para cada frame
        
        USO:
        ```python
        controller = CameraControllerV2(...)
        path = controller.generate_camera_path(duration=120.0)
        
        # Para cada frame:
        for time, x_pos, state in path:
            crop_box = controller.calculate_crop_box(x_pos, frame_height)
            # Aplicar crop
        ```
        """
        total_frames = int(duration * self.fps)
        camera_path = []
        
        for frame_num in range(total_frames):
            current_time = frame_num / self.fps
            x_pos, state = self.get_camera_position(current_time)
            camera_path.append((current_time, x_pos, state))
        
        return camera_path
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do movimento de câmera.
        
        Returns:
            Dict com estatísticas úteis para debug
        """
        if not self.meme_events:
            return {
                "total_memes": 0,
                "camera_movements": 0,
                "avg_focus_duration": 0.0
            }
        
        durations = [m.get('duration', 0.0) for m in self.meme_events]
        
        return {
            "total_memes": len(self.meme_events),
            "camera_movements": len(self.meme_events) * 2,  # Ida + volta
            "avg_focus_duration": np.mean(durations) if durations else 0.0,
            "corner_distribution": self._get_corner_distribution()
        }
    
    def _get_corner_distribution(self) -> Dict[str, int]:
        """Conta quantos memes aparecem em cada canto."""
        distribution = {'top_left': 0, 'top_right': 0, 'bottom_left': 0, 'bottom_right': 0}
        
        for meme in self.meme_events:
            position = meme.get('position', 'top_right')
            if position in distribution:
                distribution[position] += 1
        
        return distribution


# =============================================================================
# INTEGRAÇÃO COM VerticalCropper EXISTENTE
# =============================================================================

def integrate_with_vertical_cropper(
    video_path: str,
    output_path: str,
    meme_events: List[Dict],
    session_id: str
):
    """
    Integra CameraControllerV2 com VerticalCropper existente.
    
    Args:
        video_path: Vídeo de entrada
        output_path: Vídeo de saída vertical
        meme_events: Lista de eventos de memes
        session_id: ID da sessão
    
    MODIFICAÇÕES NECESSÁRIAS EM VerticalCropper.py:
    1. Adicionar parâmetro meme_events
    2. Criar CameraControllerV2
    3. Usar get_camera_position() ao invés de lógica antiga
    
    PSEUDO-CÓDIGO:
    ```python
    # Em VerticalCropper.py
    
    # Criar controlador
    controller = CameraControllerV2(
        video_width=video.width,
        video_height=video.height,
        output_width=1080,
        output_height=1920,
        meme_events=meme_events,
        fps=video.fps
    )
    
    # Para cada frame:
    for frame_num in range(total_frames):
        time = frame_num / fps
        
        # Obter posição da câmera
        camera_x, state = controller.get_camera_position(time)
        
        # Calcular crop
        x1, y1, x2, y2 = controller.calculate_crop_box(camera_x, frame.height)
        
        # Aplicar crop
        cropped = frame[y1:y2, x1:x2]
        
        # Resize para output
        resized = cv2.resize(cropped, (1080, 1920))
        
        writer.write(resized)
    ```
    """
    pass  # Implementação real será no VerticalCropper.py


# =============================================================================
# SCRIPT DE TESTE
# =============================================================================

if __name__ == "__main__":
    """
    Teste standalone do CameraControllerV2.
    
    USO:
    python Render/CameraControllerV2.py
    """
    import json
    
    print("=" * 70)
    print("TESTE DO CAMERA CONTROLLER V2")
    print("=" * 70)
    
    # Simular eventos de memes
    meme_events = [
        {
            "timestamp": 5.0,
            "position": "top_right",
            "text": "KKKK ELE MORREU",
            "duration": 4.0,
            "confidence": 0.9
        },
        {
            "timestamp": 15.0,
            "position": "bottom_left",
            "text": "FAIL ÉPICO",
            "duration": 5.0,
            "confidence": 0.85
        },
        {
            "timestamp": 25.0,
            "position": "top_left",
            "text": "WTF",
            "duration": 3.0,
            "confidence": 0.75
        }
    ]
    
    # Criar controlador
    controller = CameraControllerV2(
        video_width=1920,
        video_height=1080,
        output_width=1080,
        output_height=1920,
        meme_events=meme_events,
        fps=30.0
    )
    
    print(f"\n📹 Vídeo: 1920x1080 → 1080x1920")
    print(f"🎭 {len(meme_events)} eventos de memes")
    
    # Simular 30 segundos de vídeo
    print("\n🎬 Simulando movimento de câmera...")
    print(f"{'Tempo':<8} {'Posição X':<12} {'Estado':<20}")
    print("-" * 40)
    
    for t in np.arange(0, 30, 1.0):  # A cada 1 segundo
        x_pos, state = controller.get_camera_position(t)
        print(f"{t:6.1f}s  {x_pos:10.1f}px  {state:<20}")
    
    # Estatísticas
    print("\n📊 ESTATÍSTICAS:")
    stats = controller.get_statistics()
    print(f"   Total de memes: {stats['total_memes']}")
    print(f"   Movimentos de câmera: {stats['camera_movements']}")
    print(f"   Duração média de foco: {stats['avg_focus_duration']:.1f}s")
    print(f"   Distribuição por canto:")
    for corner, count in stats['corner_distribution'].items():
        print(f"      {corner}: {count}")
    
    print("\n✅ Teste completo!")


"""
=============================================================================
PRÓXIMOS PASSOS PARA INTEGRAÇÃO
=============================================================================

1. MODIFICAR Render/VerticalCropper.py:
   
   a) Adicionar parâmetro meme_events:
   ```python
   def render_vertical_video(video_in, video_out, meme_events=None, session_id=None):
   ```
   
   b) Se meme_events fornecido, usar CameraControllerV2:
   ```python
   if meme_events:
       controller = CameraControllerV2(...)
       # Usar controller.get_camera_position()
   else:
       # Fallback para lógica antiga
   ```

2. MODIFICAR run_pipeline.py:
   
   a) Carregar meme_events:
   ```python
   meme_events_file = f"meme_events_{session}.json"
   if os.path.exists(meme_events_file):
       with open(meme_events_file) as f:
           meme_data = json.load(f)
           meme_events = meme_data['meme_events']
   ```
   
   b) Passar para VerticalCropper:
   ```python
   render_vertical_video(
       temp_silence_path,
       short_path,
       meme_events=meme_events,
       session_id=session
   )
   ```

3. TESTAR:
   ```bash
   # Primeiro detectar memes
   python Components/MemeDetector.py input/video.mp4
   
   # Depois rodar pipeline
   python run_pipeline.py input/video.mp4
   ```

4. AJUSTAR PARÂMETROS se necessário:
   - transition_speed (se movendo muito rápido/lento)
   - smoothing_factor (se movimento não está suave)
   - corner_margin (se cortando memes)

=============================================================================
"""
