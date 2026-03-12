# Components/ClipSelector.py
"""
Seletor de clips - SEMPRE retorna TOP N clips independente do score
"""

import numpy as np


class ClipSelector:
    """Seleciona os melhores clips."""
    
    def __init__(self, profile):
        self.profile = profile
        self.thresholds = profile.get('thresholds', {})
    
    def select_clips(self, audio_features, context_analysis, meme_events, num_clips=10):
        """
        Seleciona os TOP N melhores clips.
        SEMPRE retorna num_clips (ou menos se não houver candidatos).
        
        Args:
            audio_features: Features de áudio
            context_analysis: Análise de contexto
            meme_events: Eventos de memes
            num_clips: Número de clips desejado
        
        Returns:
            Lista dos TOP N clips ordenados por score
        """
        print(f"🎯 Selecionando top {num_clips} clips...")
        
        all_candidates = []
        
        # 1. Adicionar eventos de memes
        for meme in meme_events:
            all_candidates.append({
                'start_time': meme.get('start_time', 0),
                'duration': min(60, meme.get('duration', 45)),
                'score': meme.get('score', 2.0),
                'type': 'meme',
                'meme_name': meme.get('meme_name', 'unknown'),
                'transcription': meme.get('transcription', [])
            })
        
        # 2. Adicionar highlights de contexto
        if context_analysis and 'highlights' in context_analysis:
            for highlight in context_analysis['highlights']:
                all_candidates.append({
                    'start_time': highlight.get('start_time', 0),
                    'duration': min(60, highlight.get('duration', 45)),
                    'score': highlight.get('score', 2.0),
                    'type': 'context',
                    'reason': highlight.get('reason', ''),
                    'transcription': highlight.get('transcription', [])
                })
        
        # 3. Adicionar momentos de áudio
        if audio_features and 'moments' in audio_features:
            for moment in audio_features['moments']:
                all_candidates.append({
                    'start_time': moment.get('start_time', 0),
                    'duration': min(60, moment.get('duration', 45)),
                    'score': moment.get('score', 1.5),
                    'type': 'audio',
                    'reason': 'audio_peak',
                    'transcription': []
                })
        
        print(f"   📊 {len(all_candidates)} candidatos encontrados")
        
        if not all_candidates:
            print(f"   ⚠️  NENHUM candidato! Gerando clips espaçados...")
            return self._generate_fallback_clips(num_clips)
        
        # Ordenar por score (maior primeiro)
        all_candidates.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Remover overlaps
        no_overlap = self._remove_overlaps(all_candidates)
        
        # Pegar TOP N
        if len(no_overlap) < num_clips:
            print(f"   ⚠️  Só {len(no_overlap)} clips sem overlap (pediu {num_clips})")
            final = no_overlap
        else:
            final = no_overlap[:num_clips]
        
        # Mostrar threshold como referência
        min_score = self.thresholds.get('min_score', 3.5)
        above_threshold = sum(1 for c in final if c.get('score', 0) >= min_score)
        print(f"   ℹ️  Threshold: {min_score} (informativo)")
        print(f"   ✅ {len(final)} clips selecionados ({above_threshold} acima do threshold)")
        
        return final
    
    def _remove_overlaps(self, clips):
        """Remove clips que se sobrepõem."""
        if not clips:
            return []
        
        result = []
        
        for clip in clips:
            overlaps = False
            
            for selected in result:
                clip_end = clip['start_time'] + clip['duration']
                selected_end = selected['start_time'] + selected['duration']
                
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
    
    def _generate_fallback_clips(self, num_clips, total_duration=15000):
        """Gera clips espaçados como fallback."""
        clips = []
        interval = total_duration / (num_clips + 1)
        
        for i in range(num_clips):
            clips.append({
                'start_time': interval * (i + 1),
                'duration': 45,
                'score': 1.0,
                'type': 'fallback',
                'reason': 'fallback_clip',
                'transcription': []
            })
        
        return clips
