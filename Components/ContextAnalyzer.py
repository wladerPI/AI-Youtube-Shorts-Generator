# Components/ContextAnalyzer.py
"""
=============================================================================
ANALISADOR DE CONTEXTO PROFISSIONAL - GPT + MEMES
=============================================================================

🎯 ANALISA:
1. Transcrição completa
2. Identifica seus 79 memes
3. Detecta narrativas interessantes
4. Pontua por qualidade de conteúdo

✅ INTELIGENTE:
- Entende CONTEXTO, não só palavras
- Detecta quando você usa frases específicas
- Identifica momentos com desenvolvimento
- Prefere clips com história completa

=============================================================================
"""

import json
from pathlib import Path
from Components.LanguageTasks import GetHighlights


class ContextAnalyzer:
    """
    Analisador de contexto usando GPT.
    """
    
    def __init__(self, transcription_data, video_duration_min):
        """
        Inicializa analisador.
        
        Args:
            transcription_data: Dados da transcrição
            video_duration_min: Duração do vídeo em minutos
        """
        self.transcription_data = transcription_data
        self.video_duration_min = video_duration_min
        self.context_moments = []
        
        print(f"📝 Analisador de Contexto inicializado")
        print(f"   Duração do vídeo: {video_duration_min:.1f} min")
    
    def analyze(self):
        """
        Analisa contexto com GPT.
        
        Returns:
            Lista de momentos com contexto
        """
        print("\n🤖 Analisando contexto com GPT...")
        
        # Converter transcrição para texto
        transcript_text = self._prepare_transcript()
        
        # Chamar GPT (GetHighlights do LanguageTasks)
        try:
            highlights = GetHighlights(
                transcript_text=transcript_text,
                video_duration_min=self.video_duration_min
            )
            
            print(f"   ✅ {len(highlights)} momentos detectados pelo GPT")
            
            # Processar highlights
            self.context_moments = self._process_highlights(highlights)
            
            return self.context_moments
            
        except Exception as e:
            print(f"   ❌ Erro no GPT: {e}")
            return []
    
    def _prepare_transcript(self):
        """
        Prepara transcrição para o GPT.
        
        Returns:
            Texto formatado
        """
        if isinstance(self.transcription_data, str):
            return self.transcription_data
        
        # Se for lista de segmentos
        if isinstance(self.transcription_data, list):
            segments = []
            for seg in self.transcription_data:
                if isinstance(seg, dict):
                    timestamp = seg.get('start', 0)
                    text = seg.get('text', '')
                    segments.append(f"[{timestamp:.1f}s] {text}")
                else:
                    segments.append(str(seg))
            
            return "\n".join(segments)
        
        return str(self.transcription_data)
    
    def _process_highlights(self, highlights):
        """
        Processa highlights do GPT e adiciona scores.
        
        Returns:
            Lista de momentos processados
        """
        processed = []
        
        for highlight in highlights:
            # Extrair informações
            start = highlight.get('start', 0)
            end = highlight.get('end', start + 60)
            reason = highlight.get('reason', '')
            score = highlight.get('score', 1.0)
            
            # Analisar qualidade do momento
            quality_score = self._analyze_quality(highlight, reason)
            
            # Score final
            final_score = score * quality_score
            
            processed.append({
                'timestamp': start,
                'end': end,
                'duration': end - start,
                'reason': reason,
                'score': final_score,
                'type': 'context',
                'has_meme': self._has_known_meme(reason),
                'has_narrative': len(reason) > 50  # Descrições longas = narrativa
            })
        
        return processed
    
    def _analyze_quality(self, highlight, reason):
        """
        Analisa qualidade do momento.
        
        Returns:
            Score multiplicador (0.5 - 1.5)
        """
        quality = 1.0
        
        # Bônus para momentos com suas frases
        your_phrases = [
            'puta que pariu', 'olha isso', 'meu deus do céu',
            'não acredito', 'corre corre', 'roubado',
            'má oei', 'boa', 'culpa do pele'
        ]
        
        reason_lower = reason.lower()
        if any(phrase in reason_lower for phrase in your_phrases):
            quality *= 1.3  # +30%
        
        # Bônus para risadas mencionadas
        if '[riso]' in reason_lower or 'risada' in reason_lower or 'rindo' in reason_lower:
            quality *= 1.2  # +20%
        
        # Bônus para memes conhecidos
        if self._has_known_meme(reason):
            quality *= 1.25  # +25%
        
        # Penalidade para momentos muito curtos
        duration = highlight.get('end', 0) - highlight.get('start', 0)
        if duration < 30:
            quality *= 0.8  # -20%
        
        # Bônus para momentos com boa duração (1-3 min)
        if 60 < duration < 180:
            quality *= 1.1  # +10%
        
        return min(quality, 1.5)  # Máximo 1.5x
    
    def _has_known_meme(self, text):
        """
        Verifica se contém meme conhecido.
        
        Returns:
            bool
        """
        known_memes = [
            'três dias depois', 'bob esponja',
            'você é homem ou é bixa', 'silvio santos',
            'ai que burro', 'chaves', 'da zero pra ele',
            'reprovado', 'ladrão', 'seu madruga',
            'vai dar merda', 'já acabou jessica',
            'aleluia', 'chama a policia',
            'ta amarrado', 'arca de noé', 'dilma',
            'mandioca', 'esse dedinho aqui é meu'
        ]
        
        text_lower = text.lower()
        return any(meme in text_lower for meme in known_memes)
    
    def save_results(self, output_file):
        """Salva resultados."""
        data = {
            'total_moments': len(self.context_moments),
            'video_duration_min': self.video_duration_min,
            'moments': self.context_moments
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Contexto salvo: {output_file}")


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def analyze_context(transcription_data, video_duration_min):
    """
    Analisa contexto da transcrição.
    
    Args:
        transcription_data: Dados da transcrição
        video_duration_min: Duração em minutos
    
    Returns:
        Lista de momentos com contexto
    """
    analyzer = ContextAnalyzer(transcription_data, video_duration_min)
    moments = analyzer.analyze()
    return moments
