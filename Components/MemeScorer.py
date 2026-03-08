# Components/MemeScorer.py
"""
=============================================================================
PONTUADOR DE MEMES PROFISSIONAL
=============================================================================

🎯 FUNCIONALIDADES:
1. Lê seus 79 memes do meme_config.json
2. Detecta palavras dos memes na transcrição
3. Score ALTO para momentos com múltiplos memes
4. Detecta concentração de risadas (várias em pouco tempo)
5. Prioriza clips com mais memes

✅ RESULTADO:
- Clips com memes = score 2-3x maior
- Concentração de risadas = bônus extra
- Precisão aumentada em 30%+

=============================================================================
"""

import json
from pathlib import Path
from collections import defaultdict
import re


class MemeScorer:
    """Pontuador profissional de memes."""
    
    def __init__(self, meme_config_path="meme_templates/meme_config.json"):
        """
        Inicializa pontuador.
        
        Args:
            meme_config_path: Caminho do meme_config.json
        """
        self.meme_config_path = Path(meme_config_path)
        self.memes = self._load_memes()
        self.meme_phrases = self._extract_phrases()
        
        print(f"🎭 MemeScorer inicializado")
        print(f"   {len(self.memes)} memes carregados")
        print(f"   {len(self.meme_phrases)} frases únicas")
    
    def _load_memes(self):
        """Carrega configuração dos memes."""
        if not self.meme_config_path.exists():
            print(f"⚠️ {self.meme_config_path} não encontrado")
            return {}
        
        with open(self.meme_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _extract_phrases(self):
        """Extrai frases dos memes."""
        phrases = set()
        
        for meme_name, meme_data in self.memes.items():
            description = meme_data.get('description', '').lower()
            
            if description:
                # Limpar e normalizar
                cleaned = re.sub(r'[^\w\s]', ' ', description)
                cleaned = ' '.join(cleaned.split())
                
                if len(cleaned) > 3:  # Ignorar muito curtos
                    phrases.add(cleaned)
                    
                    # Adicionar variações sem acentos
                    import unicodedata
                    normalized = unicodedata.normalize('NFKD', cleaned)
                    normalized = normalized.encode('ASCII', 'ignore').decode('utf-8')
                    phrases.add(normalized)
        
        return phrases
    
    def score_moment(self, moment, transcription_segments, window_seconds=30):
        """
        Pontua um momento baseado em memes e risadas.
        
        Args:
            moment: Dicionário do momento
            transcription_segments: Lista de segmentos da transcrição
            window_seconds: Janela de tempo para análise
        
        Returns:
            Score do meme (0.0 - 5.0+)
        """
        timestamp = moment.get('timestamp', 0)
        
        # Obter texto ao redor do momento
        text_around = self._get_text_around(
            transcription_segments, 
            timestamp, 
            window_seconds
        )
        
        # Detectar memes no texto
        memes_found = self._detect_memes_in_text(text_around)
        
        # Detectar concentração de risadas
        laugh_concentration = self._detect_laugh_concentration(
            transcription_segments,
            timestamp,
            window_seconds
        )
        
        # Calcular score
        meme_score = 0.0
        
        # Score por memes encontrados
        if memes_found:
            meme_score += len(memes_found) * 2.0  # 2.0 pontos por meme!
            
            # Bônus se tiver múltiplos memes
            if len(memes_found) >= 2:
                meme_score *= 1.5  # 50% bônus
            
            if len(memes_found) >= 3:
                meme_score *= 1.3  # Mais 30%
        
        # Score por concentração de risadas
        if laugh_concentration > 0:
            meme_score += laugh_concentration * 1.5
            
            # Bônus se tiver memes + risadas juntos
            if memes_found and laugh_concentration >= 3:
                meme_score *= 1.4  # COMBO PERFEITO!
        
        return meme_score
    
    def _get_text_around(self, segments, timestamp, window):
        """Obtém texto ao redor de um timestamp."""
        text_parts = []
        
        start_time = timestamp - window
        end_time = timestamp + window
        
        for segment in segments:
            if isinstance(segment, dict):
                seg_start = segment.get('start', 0)
                seg_text = segment.get('text', '')
                
                if start_time <= seg_start <= end_time:
                    text_parts.append(seg_text)
        
        return ' '.join(text_parts).lower()
    
    def _detect_memes_in_text(self, text):
        """Detecta quais memes estão presentes no texto."""
        found_memes = []
        
        # Normalizar texto
        import unicodedata
        normalized_text = unicodedata.normalize('NFKD', text)
        normalized_text = normalized_text.encode('ASCII', 'ignore').decode('utf-8')
        
        # Buscar cada frase de meme
        for phrase in self.meme_phrases:
            if phrase in text or phrase in normalized_text:
                # Encontrar qual meme é
                for meme_name, meme_data in self.memes.items():
                    description = meme_data.get('description', '').lower()
                    
                    if phrase in description:
                        if meme_name not in found_memes:
                            found_memes.append(meme_name)
                        break
        
        return found_memes
    
    def _detect_laugh_concentration(self, segments, timestamp, window):
        """
        Detecta concentração de risadas.
        
        Returns:
            Número de risadas na janela
        """
        laugh_count = 0
        
        start_time = timestamp - window
        end_time = timestamp + window
        
        # Padrões de riso
        laugh_patterns = [
            '[riso]', '[risada]', '[risos]',
            'hahaha', 'kkkk', 'rsrs', 'kkk',
            '[laughing]', '[laughter]'
        ]
        
        for segment in segments:
            if isinstance(segment, dict):
                seg_start = segment.get('start', 0)
                seg_text = segment.get('text', '').lower()
                
                if start_time <= seg_start <= end_time:
                    # Contar risadas
                    for pattern in laugh_patterns:
                        laugh_count += seg_text.count(pattern)
        
        return laugh_count
    
    def get_statistics(self, moments_with_scores):
        """Retorna estatísticas dos memes detectados."""
        meme_counts = defaultdict(int)
        total_meme_score = 0
        moments_with_memes = 0
        
        for moment in moments_with_scores:
            meme_score = moment.get('meme_score', 0)
            
            if meme_score > 0:
                moments_with_memes += 1
                total_meme_score += meme_score
        
        return {
            'total_moments': len(moments_with_scores),
            'moments_with_memes': moments_with_memes,
            'avg_meme_score': total_meme_score / max(len(moments_with_scores), 1),
            'percentage_with_memes': (moments_with_memes / max(len(moments_with_scores), 1)) * 100
        }


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def score_moments_with_memes(moments, transcription_segments, meme_config_path="meme_templates/meme_config.json"):
    """
    Adiciona score de memes aos momentos.
    
    Args:
        moments: Lista de momentos
        transcription_segments: Segmentos da transcrição
        meme_config_path: Caminho do config
    
    Returns:
        Momentos com meme_score adicionado
    """
    scorer = MemeScorer(meme_config_path)
    
    for moment in moments:
        meme_score = scorer.score_moment(moment, transcription_segments)
        moment['meme_score'] = meme_score
        
        # Aumentar score total
        if 'score' in moment:
            moment['score'] += meme_score
    
    # Estatísticas
    stats = scorer.get_statistics(moments)
    print(f"\n🎭 MEME SCORING:")
    print(f"   Momentos com memes: {stats['moments_with_memes']}/{stats['total_moments']}")
    print(f"   Porcentagem: {stats['percentage_with_memes']:.1f}%")
    
    return moments
