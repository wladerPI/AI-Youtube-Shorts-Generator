# Components/ClipSelector.py
"""
=============================================================================
SELETOR DE CLIPS PROFISSIONAL - COMBINAÇÃO INTELIGENTE
=============================================================================

🎯 COMBINA:
1. Momentos de áudio (risadas, energia)
2. Momentos de contexto (GPT, narrativas)
3. Remove duplicatas
4. Seleciona os melhores

✅ INTELIGENTE:
- Prefere clips com ÁUDIO + CONTEXTO
- Evita sobreposições
- Mantém duração 1-4 minutos
- Ordena por qualidade

=============================================================================
"""

import json
from pathlib import Path


class ClipSelector:
    """
    Seletor inteligente de clips.
    """
    
    def __init__(self, audio_moments, context_moments, max_clips=50):
        """
        Inicializa seletor.
        
        Args:
            audio_moments: Momentos detectados no áudio
            context_moments: Momentos detectados por contexto
            max_clips: Número máximo de clips
        """
        self.audio_moments = audio_moments or []
        self.context_moments = context_moments or []
        self.max_clips = max_clips
        self.selected_clips = []
        
        print(f"🎬 Seletor de Clips inicializado")
        print(f"   Momentos de áudio: {len(self.audio_moments)}")
        print(f"   Momentos de contexto: {len(self.context_moments)}")
        print(f"   Clips alvo: {max_clips}")
    
    def select(self, min_duration=45, max_duration=240, min_gap=30):
        """
        Seleciona os melhores clips.
        
        Args:
            min_duration: Duração mínima (segundos)
            max_duration: Duração máxima (segundos)
            min_gap: Espaçamento mínimo entre clips (segundos)
        
        Returns:
            Lista de clips selecionados
        """
        print("\n🎯 Selecionando clips...")
        
        # 1. Combinar momentos
        print("   [1/5] Combinando momentos...")
        combined = self._combine_moments()
        print(f"      ✅ {len(combined)} momentos combinados")
        
        # 2. Expandir para clips com duração adequada
        print("   [2/5] Expandindo para clips...")
        expanded = self._expand_to_clips(combined, min_duration, max_duration)
        print(f"      ✅ {len(expanded)} clips expandidos")
        
        # 3. Remover sobreposições
        print("   [3/5] Removendo sobreposições...")
        no_overlap = self._remove_overlaps(expanded, min_gap)
        print(f"      ✅ {len(no_overlap)} clips sem sobreposição")
        
        # 4. Ordenar por score
        print("   [4/5] Ordenando por qualidade...")
        sorted_clips = sorted(no_overlap, key=lambda x: x['score'], reverse=True)
        
        # 5. Selecionar top N
        print("   [5/5] Selecionando melhores...")
        self.selected_clips = sorted_clips[:self.max_clips]
        
        # Estatísticas
        with_audio = sum(1 for c in self.selected_clips if c.get('has_audio'))
        with_context = sum(1 for c in self.selected_clips if c.get('has_context'))
        with_both = sum(1 for c in self.selected_clips if c.get('has_audio') and c.get('has_context'))
        
        print(f"\n   ✅ {len(self.selected_clips)} clips selecionados:")
        print(f"      Com áudio: {with_audio}")
        print(f"      Com contexto: {with_context}")
        print(f"      Com ambos: {with_both} 🎯")
        
        return self.selected_clips
    
    def _combine_moments(self):
        """
        Combina momentos de áudio e contexto.
        
        Returns:
            Lista de momentos combinados
        """
        combined = []
        
        # Adicionar momentos de áudio
        for audio_m in self.audio_moments:
            combined.append({
                'timestamp': audio_m['timestamp'],
                'score': audio_m['score'],
                'type': 'audio',
                'has_audio': True,
                'has_context': False,
                'has_laugh': audio_m.get('has_laugh', False),
                'has_energy': audio_m.get('has_energy', False),
                'reasons': audio_m.get('reasons', [])
            })
        
        # Adicionar momentos de contexto
        for context_m in self.context_moments:
            # Verificar se já existe momento de áudio próximo
            merged = False
            for existing in combined:
                if abs(existing['timestamp'] - context_m['timestamp']) < 30:
                    # Mesclar!
                    existing['has_context'] = True
                    existing['score'] += context_m['score']
                    existing['score'] *= 1.3  # BÔNUS por ter áudio + contexto!
                    existing['reasons'].append(context_m.get('reason', ''))
                    
                    if context_m.get('has_meme'):
                        existing['has_meme'] = True
                    
                    merged = True
                    break
            
            if not merged:
                # Adicionar como novo
                combined.append({
                    'timestamp': context_m['timestamp'],
                    'score': context_m['score'],
                    'type': 'context',
                    'has_audio': False,
                    'has_context': True,
                    'has_meme': context_m.get('has_meme', False),
                    'has_narrative': context_m.get('has_narrative', False),
                    'reasons': [context_m.get('reason', '')]
                })
        
        return combined
    
    def _expand_to_clips(self, moments, min_duration, max_duration):
        """
        Expande momentos para clips com duração adequada.
        
        Returns:
            Lista de clips
        """
        clips = []
        
        for moment in moments:
            timestamp = moment['timestamp']
            
            # Determinar duração baseado no score e tipo
            if moment['has_audio'] and moment['has_context']:
                # Melhor tipo: áudio + contexto
                target_duration = 120  # 2 minutos
            elif moment['has_context']:
                # Contexto: pode ser mais longo
                target_duration = 90  # 1.5 minutos
            else:
                # Só áudio: mais curto
                target_duration = 60  # 1 minuto
            
            # Ajustar por narrativa
            if moment.get('has_narrative'):
                target_duration = min(target_duration * 1.5, max_duration)
            
            # Centralizar ao redor do momento
            start = max(0, timestamp - (target_duration / 2))
            end = start + target_duration
            
            # Garantir limites
            duration = end - start
            if duration < min_duration:
                end = start + min_duration
            elif duration > max_duration:
                end = start + max_duration
            
            clips.append({
                'start': start,
                'end': end,
                'duration': end - start,
                'timestamp': timestamp,
                'score': moment['score'],
                'has_audio': moment['has_audio'],
                'has_context': moment['has_context'],
                'has_laugh': moment.get('has_laugh', False),
                'has_meme': moment.get('has_meme', False),
                'reasons': moment['reasons']
            })
        
        return clips
    
    def _remove_overlaps(self, clips, min_gap):
        """
        Remove clips sobrepostos.
        
        Returns:
            Lista sem sobreposições
        """
        if not clips:
            return []
        
        # Ordenar por score
        sorted_clips = sorted(clips, key=lambda x: x['score'], reverse=True)
        
        selected = []
        for clip in sorted_clips:
            # Verificar sobreposição com já selecionados
            overlap = False
            for sel in selected:
                # Verificar se sobrepõe
                if not (clip['end'] + min_gap < sel['start'] or 
                       sel['end'] + min_gap < clip['start']):
                    overlap = True
                    break
            
            if not overlap:
                selected.append(clip)
        
        # Reordenar por timestamp
        selected.sort(key=lambda x: x['start'])
        
        return selected
    
    def save_results(self, output_file):
        """Salva clips selecionados."""
        data = {
            'total_clips': len(self.selected_clips),
            'clips': self.selected_clips,
            'statistics': {
                'with_audio': sum(1 for c in self.selected_clips if c.get('has_audio')),
                'with_context': sum(1 for c in self.selected_clips if c.get('has_context')),
                'with_both': sum(1 for c in self.selected_clips if c.get('has_audio') and c.get('has_context')),
                'with_laugh': sum(1 for c in self.selected_clips if c.get('has_laugh')),
                'with_meme': sum(1 for c in self.selected_clips if c.get('has_meme'))
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Clips salvos: {output_file}")


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def select_clips(audio_moments, context_moments, max_clips=50):
    """
    Seleciona os melhores clips.
    
    Args:
        audio_moments: Momentos de áudio
        context_moments: Momentos de contexto
        max_clips: Número máximo
    
    Returns:
        Lista de clips selecionados
    """
    selector = ClipSelector(audio_moments, context_moments, max_clips)
    clips = selector.select()
    return clips
