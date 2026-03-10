# Components/ClipSelector.py
"""
Seletor de clips V3 com priorização de memes e thresholds do perfil.
"""

import numpy as np
from datetime import timedelta


class ClipSelector:
    """Seleciona os melhores clips baseado em múltiplos fatores."""
    
    def __init__(self, profile):
        """
        Inicializa seletor com perfil.
        
        Args:
            profile: Perfil com thresholds e configurações
        """
        self.profile = profile
        self.thresholds = profile.get('thresholds', {})
    
    def select_clips(self, audio_features, context_analysis, meme_events, num_clips=10):
        """
        Seleciona os melhores clips.
        
        Args:
            audio_features: Features de áudio analisadas
            context_analysis: Análise de contexto (GPT)
            meme_events: Eventos de memes detectados
            num_clips: Número de clips a selecionar
        
        Returns:
            Lista de clips selecionados ordenados por score
        """
        print(f"🎯 Selecionando top {num_clips} clips...")
        
        # Combinar todos os eventos
        all_candidates = []
        
        # Adicionar eventos de memes (prioridade alta)
        for meme in meme_events:
            all_candidates.append({
                'start_time': meme['start_time'],
                'duration': min(60, meme.get('duration', 45)),  # Max 60s
                'score': meme['score'],
                'type': 'meme',
                'meme_name': meme.get('meme_name', 'unknown'),
                'transcription': meme.get('transcription', [])
            })
        
        # Adicionar momentos de contexto
        if context_analysis and 'highlights' in context_analysis:
            for highlight in context_analysis['highlights']:
                all_candidates.append({
                    'start_time': highlight['start_time'],
                    'duration': min(60, highlight.get('duration', 45)),
                    'score': highlight['score'],
                    'type': 'context',
                    'reason': highlight.get('reason', ''),
                    'transcription': highlight.get('transcription', [])
                })
        
        # Filtrar por threshold mínimo
        min_score = self.thresholds.get('min_score', 3.5)
        
        filtered = [c for c in all_candidates if c['score'] >= min_score]
        
        print(f"   📊 {len(all_candidates)} candidatos → {len(filtered)} acima de {min_score}")
        
        # Ordenar por score
        filtered.sort(key=lambda x: x['score'], reverse=True)
        
        # Remover overlaps
        selected = self._remove_overlaps(filtered)
        
        # Retornar top N
        final = selected[:num_clips]
        
        print(f"   ✅ {len(final)} clips selecionados")
        
        return final
    
    def _remove_overlaps(self, clips):
        """Remove clips que se sobrepõem, mantendo os de maior score."""
        if not clips:
            return []
        
        result = []
        
        for clip in clips:
            overlaps = False
            
            for selected in result:
                # Verificar overlap
                clip_end = clip['start_time'] + clip['duration']
                selected_end = selected['start_time'] + selected['duration']
                
                # Se overlap > 50% da duração menor
                overlap_start = max(clip['start_time'], selected['start_time'])
                overlap_end = min(clip_end, selected_end)
                overlap_duration = max(0, overlap_end - overlap_start)
                
                min_duration = min(clip['duration'], selected['duration'])
                
                if overlap_duration > min_duration * 0.5:
                    overlaps = True
                    break
            
            if not overlaps:
                result.append(clip)
        
        return result
