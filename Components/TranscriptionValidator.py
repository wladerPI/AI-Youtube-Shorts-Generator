# Components/TranscriptionValidator.py
"""
=============================================================================
VALIDADOR DE TRANSCRIÇÃO PROFISSIONAL
=============================================================================

🎯 VERIFICA:
1. Qualidade da transcrição
2. Palavras mal transcritas
3. Taxa de confiança
4. Cobertura de áudio

✅ ALERTA:
- Se transcrição está ruim
- Se precisa melhorar qualidade do áudio
- Se Whisper teve problemas

=============================================================================
"""

import re
from collections import Counter


class TranscriptionValidator:
    """Validador de qualidade de transcrição."""
    
    def __init__(self):
        """Inicializa validador."""
        # Palavras que indicam problemas
        self.garbage_patterns = [
            r'[^\w\s\[\]]',  # Caracteres estranhos
            r'\b[a-z]{15,}\b',  # Palavras muito longas
            r'([a-z])\1{4,}',  # Repetições (aaaaa)
        ]
        
        # Palavras comuns em português (esperadas)
        self.common_words = {
            'o', 'a', 'de', 'e', 'do', 'da', 'em', 'um', 'para',
            'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por',
            'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele',
            'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando',
            'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só',
            'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era',
            'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem',
            'nas', 'me', 'esse', 'eles', 'estão', 'você', 'tinha',
            'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha',
            'têm', 'numa', 'pelos', 'elas', 'havia', 'seja', 'qual',
            'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses',
            'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês',
            'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus',
            'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas',
            'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles',
            'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos',
            'estão', 'estive', 'esteve', 'estivemos', 'estiveram',
            'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos',
            'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos',
            'estivessem', 'estiver', 'estivermos', 'estiverem'
        }
    
    def validate(self, transcription_segments):
        """
        Valida qualidade da transcrição.
        
        Args:
            transcription_segments: Segmentos da transcrição
        
        Returns:
            dict com métricas de qualidade
        """
        print("\n📋 Validando transcrição...")
        
        # Extrair todo o texto
        full_text = self._extract_text(transcription_segments)
        
        # Análises
        word_count = len(full_text.split())
        garbage_count = self._count_garbage(full_text)
        common_word_ratio = self._calculate_common_word_ratio(full_text)
        avg_word_length = self._average_word_length(full_text)
        repetition_score = self._detect_repetitions(full_text)
        
        # Calcular score de qualidade (0-100)
        quality_score = 100
        
        # Penalidades
        if garbage_count > word_count * 0.05:  # > 5% lixo
            quality_score -= 30
        
        if common_word_ratio < 0.30:  # < 30% palavras comuns
            quality_score -= 20
        
        if avg_word_length > 8:  # Palavras muito longas
            quality_score -= 15
        
        if repetition_score > 0.1:  # Muitas repetições
            quality_score -= 15
        
        quality_score = max(0, quality_score)
        
        # Determinar status
        if quality_score >= 80:
            status = "✅ EXCELENTE"
        elif quality_score >= 60:
            status = "⚠️ BOA (alguns problemas)"
        elif quality_score >= 40:
            status = "⚠️ RAZOÁVEL (vários problemas)"
        else:
            status = "❌ RUIM (muitos problemas)"
        
        result = {
            'quality_score': quality_score,
            'status': status,
            'word_count': word_count,
            'garbage_count': garbage_count,
            'common_word_ratio': common_word_ratio,
            'avg_word_length': avg_word_length,
            'repetition_score': repetition_score
        }
        
        # Imprimir resultado
        print(f"   Status: {status}")
        print(f"   Score: {quality_score}/100")
        print(f"   Palavras: {word_count}")
        print(f"   Lixo detectado: {garbage_count}")
        print(f"   Palavras comuns: {common_word_ratio*100:.1f}%")
        
        if quality_score < 60:
            print(f"\n   ⚠️ RECOMENDAÇÕES:")
            if garbage_count > word_count * 0.05:
                print(f"      - Muitas palavras malformadas")
            if common_word_ratio < 0.30:
                print(f"      - Poucas palavras reconhecidas")
            print(f"      - Considere melhorar qualidade do áudio")
            print(f"      - Ou usar modelo Whisper maior (medium/large)")
        
        return result
    
    def _extract_text(self, segments):
        """Extrai texto completo."""
        if isinstance(segments, str):
            return segments.lower()
        
        parts = []
        for seg in segments:
            if isinstance(seg, dict):
                text = seg.get('text', '')
                parts.append(text)
        
        return ' '.join(parts).lower()
    
    def _count_garbage(self, text):
        """Conta palavras/padrões que indicam lixo."""
        garbage_count = 0
        
        for pattern in self.garbage_patterns:
            matches = re.findall(pattern, text)
            garbage_count += len(matches)
        
        return garbage_count
    
    def _calculate_common_word_ratio(self, text):
        """Calcula proporção de palavras comuns."""
        words = text.split()
        if not words:
            return 0
        
        common_count = sum(1 for w in words if w in self.common_words)
        return common_count / len(words)
    
    def _average_word_length(self, text):
        """Calcula comprimento médio das palavras."""
        words = [w for w in text.split() if w.isalpha()]
        if not words:
            return 0
        
        return sum(len(w) for w in words) / len(words)
    
    def _detect_repetitions(self, text):
        """Detecta taxa de repetições excessivas."""
        words = text.split()
        if len(words) < 10:
            return 0
        
        # Contar palavras únicas vs total
        unique_words = set(words)
        repetition_score = 1 - (len(unique_words) / len(words))
        
        return repetition_score


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def validate_transcription(transcription_segments):
    """
    Valida qualidade da transcrição.
    
    Args:
        transcription_segments: Segmentos
    
    Returns:
        dict com métricas
    """
    validator = TranscriptionValidator()
    return validator.validate(transcription_segments)
