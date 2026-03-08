# Components/ClipSelector_V2.py
"""
=============================================================================
SELETOR DE CLIPS V2 - COM PRIORIDADE DE MEMES
=============================================================================

🎯 MELHORIAS:
1. Integra MemeScorer
2. Prioriza clips com múltiplos memes
3. Bônus para concentração de risadas
4. Usa thresholds do perfil
5. Sistema de pontuação profissional

✅ SCORE FINAL:
Score = (Áudio + Contexto + Memes + Risadas) × Bônus × Profile_Thresholds

=============================================================================
"""

from typing import List, Dict
import json


class ClipSelectorV2:
    """Seletor de clips profissional com memes."""
    
    def __init__(self, 
                 audio_moments: List[Dict],
                 context_moments: List[Dict],
                 meme_moments: List[Dict],  # NOVO!
                 max_clips: int = 50,
                 profile_thresholds: Dict = None):
        """
        Inicializa seletor.
        
        Args:
            audio_moments: Momentos de áudio
            context_moments: Momentos de contexto
            meme_moments: Momentos com memes (NOVO!)
            max_clips: Número máximo de clips
            profile_thresholds: Thresholds do perfil
        """
        self.audio_moments = audio_moments
        self.context_moments = context_moments
        self.meme_moments = meme_moments  # NOVO!
        self.max_clips = max_clips
        
        # Thresholds do perfil
        self.thresholds = profile_thresholds or {
            'min_score': 3.0,
            'min_meme_score': 2.0,
            'min_laugh_concentration': 2,
            'duracao_min': 45,
            'duracao_max': 240
        }
        
        print(f"🎬 Seletor de Clips V2 inicializado")
        print(f"   Momentos de áudio: {len(audio_moments)}")
        print(f"   Momentos de contexto: {len(context_moments)}")
        print(f"   Momentos com memes: {len(meme_moments)}")  # NOVO!
        print(f"   Clips alvo: {max_clips}")
        print(f"   Min score: {self.thresholds['min_score']}")
        print(f"   Min meme score: {self.thresholds['min_meme_score']}")  # NOVO!
    
    def select_clips(self) -> List[Dict]:
        """
        Seleciona melhores clips.
        
        Returns:
            Lista de clips selecionados
        """
        print(f"\n🎯 Selecionando clips...")
        
        # PASSO 1: Combinar momentos
        print(f"   [1/6] Combinando momentos...")
        combined = self._combine_moments()
        print(f"      ✅ {len(combined)} momentos combinados")
        
        # PASSO 2: Adicionar scores de memes
        print(f"   [2/6] Adicionando scores de memes...")
        combined = self._add_meme_scores(combined)
        print(f"      ✅ Meme scores adicionados")
        
        # PASSO 3: Expandir para clips
        print(f"   [3/6] Expandindo para clips...")
        clips = self._expand_to_clips(combined)
        print(f"      ✅ {len(clips)} clips expandidos")
        
        # PASSO 4: Filtrar por thresholds
        print(f"   [4/6] Filtrando por qualidade...")
        clips = self._filter_by_thresholds(clips)
        print(f"      ✅ {len(clips)} clips qualificados")
        
        # PASSO 5: Remover sobreposições
        print(f"   [5/6] Removendo sobreposições...")
        clips = self._remove_overlaps(clips)
        print(f"      ✅ {len(clips)} clips sem sobreposição")
        
        # PASSO 6: Ordenar e selecionar melhores
        print(f"   [6/6] Selecionando melhores...")
        clips = sorted(clips, key=lambda x: x['score'], reverse=True)
        selected = clips[:self.max_clips]
        
        # Estatísticas
        with_audio = sum(1 for c in selected if c.get('has_audio'))
        with_context = sum(1 for c in selected if c.get('has_context'))
        with_memes = sum(1 for c in selected if c.get('meme_score', 0) > 0)  # NOVO!
        with_all = sum(1 for c in selected if c.get('has_audio') and c.get('has_context') and c.get('meme_score', 0) > 0)
        
        print(f"\n   ✅ {len(selected)} clips selecionados:")
        print(f"      Com áudio: {with_audio}")
        print(f"      Com contexto: {with_context}")
        print(f"      Com memes: {with_memes} 🎭")  # NOVO!
        print(f"      COMBO completo: {with_all} 🎯")  # NOVO!
        
        return selected
    
    def _combine_moments(self) -> List[Dict]:
        """Combina momentos de diferentes fontes."""
        combined = []
        proximity_threshold = 30  # segundos
        
        # Adicionar momentos de áudio
        for moment in self.audio_moments:
            combined.append({
                **moment,
                'has_audio': True,
                'has_context': False,
                'has_memes': False
            })
        
        # Adicionar ou mesclar momentos de contexto
        for context_moment in self.context_moments:
            # Procurar momento próximo
            merged = False
            for existing in combined:
                if abs(existing['timestamp'] - context_moment['timestamp']) < proximity_threshold:
                    # Mesclar
                    existing['score'] += context_moment.get('score', 0)
                    existing['has_context'] = True
                    existing['reasons'] = existing.get('reasons', []) + context_moment.get('reasons', [])
                    merged = True
                    break
            
            if not merged:
                combined.append({
                    **context_moment,
                    'has_audio': False,
                    'has_context': True,
                    'has_memes': False
                })
        
        return combined
    
    def _add_meme_scores(self, moments: List[Dict]) -> List[Dict]:
        """Adiciona scores de memes aos momentos."""
        proximity_threshold = 30  # segundos
        
        for moment in moments:
            moment['meme_score'] = 0
            moment['meme_names'] = []
            
            # Procurar memes próximos
            for meme_moment in self.meme_moments:
                if abs(moment['timestamp'] - meme_moment['timestamp']) < proximity_threshold:
                    # Adicionar score do meme
                    meme_score = meme_moment.get('meme_score', 0)
                    moment['meme_score'] += meme_score
                    
                    # Adicionar nome do meme
                    if meme_moment.get('meme_names'):
                        moment['meme_names'].extend(meme_moment['meme_names'])
            
            # Se tem memes, marcar e aumentar score total
            if moment['meme_score'] > 0:
                moment['has_memes'] = True
                moment['score'] += moment['meme_score']
                
                # BÔNUS EXTRA para momentos com múltiplos memes
                unique_memes = len(set(moment['meme_names']))
                if unique_memes >= 2:
                    moment['score'] *= 1.3  # 30% bônus
                if unique_memes >= 3:
                    moment['score'] *= 1.2  # Mais 20%
        
        return moments
    
    def _expand_to_clips(self, moments: List[Dict]) -> List[Dict]:
        """Expande momentos para clips com duração."""
        clips = []
        
        for moment in moments:
            # Duração padrão
            duration = self.thresholds['duracao_min']
            
            # Ajustar duração se tiver memes (mais contexto)
            if moment.get('has_memes'):
                duration = min(90, duration + 30)  # +30s para memes
            
            # Ajustar duração se tiver contexto
            if moment.get('has_context'):
                duration = min(120, duration + 30)  # +30s para contexto
            
            # Limitar duração máxima
            duration = min(duration, self.thresholds['duracao_max'])
            
            clip = {
                **moment,
                'start': max(0, moment['timestamp'] - duration / 2),
                'end': moment['timestamp'] + duration / 2,
                'duration': duration
            }
            
            clips.append(clip)
        
        return clips
    
    def _filter_by_thresholds(self, clips: List[Dict]) -> List[Dict]:
        """Filtra clips por thresholds de qualidade."""
        filtered = []
        
        for clip in clips:
            # Score mínimo
            if clip['score'] < self.thresholds['min_score']:
                continue
            
            # Se tem memes, verificar meme score mínimo
            if clip.get('has_memes') and clip.get('meme_score', 0) < self.thresholds['min_meme_score']:
                continue
            
            # Duração
            if not (self.thresholds['duracao_min'] <= clip['duration'] <= self.thresholds['duracao_max']):
                continue
            
            filtered.append(clip)
        
        return filtered
    
    def _remove_overlaps(self, clips: List[Dict]) -> List[Dict]:
        """Remove sobreposições mantendo os melhores."""
        # Ordenar por score (decrescente)
        sorted_clips = sorted(clips, key=lambda x: x['score'], reverse=True)
        
        selected = []
        min_gap = 30  # segundos
        
        for clip in sorted_clips:
            # Verificar sobreposição com clips já selecionados
            overlap = False
            for existing in selected:
                if not (clip['end'] < existing['start'] - min_gap or 
                       clip['start'] > existing['end'] + min_gap):
                    overlap = True
                    break
            
            if not overlap:
                selected.append(clip)
        
        return selected


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def select_clips_v2(audio_moments, context_moments, meme_moments, max_clips=50, profile_thresholds=None):
    """
    Seleciona clips V2.
    
    Args:
        audio_moments: Momentos de áudio
        context_moments: Momentos de contexto
        meme_moments: Momentos com memes
        max_clips: Número máximo
        profile_thresholds: Thresholds do perfil
    
    Returns:
        Lista de clips selecionados
    """
    selector = ClipSelectorV2(
        audio_moments=audio_moments,
        context_moments=context_moments,
        meme_moments=meme_moments,
        max_clips=max_clips,
        profile_thresholds=profile_thresholds
    )
    
    return selector.select_clips()
