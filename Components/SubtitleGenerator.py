# Components/SubtitleGenerator.py
"""
=============================================================================
GERADOR DE LEGENDAS PROFISSIONAL - PT-BR
=============================================================================

✨ FEATURES:
- Word-level timing perfeito (milissegundos)
- PT-BR nativo
- Formatação CapCut-ready
- Quebra inteligente de linhas
- Detecção de frases completas
- Exporta .SRT + .ASS

=============================================================================
"""

import re
from pathlib import Path
from datetime import timedelta


class SubtitleGenerator:
    """Gera legendas profissionais em PT-BR."""
    
    def __init__(self, max_chars_per_line=42, max_lines=2):
        """
        Inicializa gerador.
        
        Args:
            max_chars_per_line: Máximo de caracteres por linha
            max_lines: Máximo de linhas por legenda
        """
        self.max_chars_per_line = max_chars_per_line
        self.max_lines = max_lines
    
    def generate_srt(self, transcription_segments, output_file, min_duration=0.8):
        """
        Gera arquivo .SRT a partir da transcrição Whisper.
        
        Args:
            transcription_segments: Segmentos com word-level timestamps
            output_file: Caminho do arquivo .srt
            min_duration: Duração mínima de cada legenda (segundos)
        
        Returns:
            Caminho do arquivo gerado
        """
        print(f"📝 Gerando legendas: {Path(output_file).name}")
        
        subtitles = []
        
        # Processar segmentos
        for segment in transcription_segments:
            if not isinstance(segment, dict):
                continue
            
            # Obter palavras com timestamps
            words = segment.get('words', [])
            
            if not words and segment.get('text'):
                # Fallback: usar timestamps do segmento
                words = [{
                    'word': word,
                    'start': segment['start'],
                    'end': segment['end']
                } for word in segment['text'].split()]
            
            # Agrupar palavras em legendas
            current_subtitle = []
            current_start = None
            current_chars = 0
            
            for i, word_data in enumerate(words):
                if isinstance(word_data, dict):
                    word = word_data.get('word', '').strip()
                    start = word_data.get('start', 0)
                    end = word_data.get('end', 0)
                else:
                    continue
                
                if not word:
                    continue
                
                # Iniciar nova legenda
                if current_start is None:
                    current_start = start
                
                # Adicionar palavra
                current_subtitle.append(word)
                current_chars += len(word) + 1
                
                # Verificar se deve quebrar linha
                should_break = (
                    current_chars >= self.max_chars_per_line or
                    self._is_sentence_end(word) or
                    i == len(words) - 1 or
                    (i < len(words) - 1 and 
                     isinstance(words[i + 1], dict) and
                     words[i + 1].get('start', 0) - end > 0.5)
                )
                
                if should_break and current_subtitle:
                    # Criar legenda
                    text = ' '.join(current_subtitle)
                    
                    # Garantir duração mínima
                    duration = max(end - current_start, min_duration)
                    
                    subtitles.append({
                        'start': current_start,
                        'end': current_start + duration,
                        'text': text
                    })
                    
                    # Resetar
                    current_subtitle = []
                    current_start = None
                    current_chars = 0
        
        # Escrever arquivo .SRT
        self._write_srt(subtitles, output_file)
        
        print(f"   ✅ {len(subtitles)} legendas geradas")
        
        return output_file
    
    def _is_sentence_end(self, word):
        """Verifica se palavra termina sentença."""
        return bool(re.search(r'[.!?;]$', word))
    
    def _write_srt(self, subtitles, output_file):
        """Escreve arquivo .SRT."""
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(subtitles, 1):
                # Número da legenda
                f.write(f"{i}\n")
                
                # Timestamps
                start_time = self._format_timestamp(sub['start'])
                end_time = self._format_timestamp(sub['end'])
                f.write(f"{start_time} --> {end_time}\n")
                
                # Texto
                text = self._format_text(sub['text'])
                f.write(f"{text}\n\n")
    
    def _format_timestamp(self, seconds):
        """Formata timestamp para .SRT (HH:MM:SS,mmm)."""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_text(self, text):
        """Formata texto da legenda."""
        # Limpar espaços extras
        text = ' '.join(text.split())
        
        # Quebrar em linhas se muito longo
        if len(text) <= self.max_chars_per_line:
            return text
        
        # Quebrar em 2 linhas
        words = text.split()
        mid = len(words) // 2
        
        line1 = ' '.join(words[:mid])
        line2 = ' '.join(words[mid:])
        
        return f"{line1}\n{line2}"
    
    def generate_ass(self, srt_file, output_file=None, style='default'):
        """
        Converte .SRT para .ASS com estilo.
        
        Args:
            srt_file: Arquivo .srt de entrada
            output_file: Arquivo .ass de saída (opcional)
            style: Estilo ('default', 'hormozi', 'mrbeast', 'gaming')
        
        Returns:
            Caminho do arquivo .ass
        """
        if output_file is None:
            output_file = str(Path(srt_file).with_suffix('.ass'))
        
        # Estilos pré-definidos
        styles = {
            'default': {
                'fontsize': 24,
                'primarycolour': '&H00FFFFFF',
                'bold': '-1',
                'outline': 2
            },
            'hormozi': {
                'fontsize': 28,
                'primarycolour': '&H0000FFFF',  # Amarelo
                'bold': '-1',
                'outline': 3
            },
            'mrbeast': {
                'fontsize': 26,
                'primarycolour': '&H00FFFFFF',
                'bold': '-1',
                'outline': 4,
                'shadow': 2
            },
            'gaming': {
                'fontsize': 24,
                'primarycolour': '&H0000FF00',  # Verde neon
                'bold': '-1',
                'outline': 2
            }
        }
        
        selected_style = styles.get(style, styles['default'])
        
        # Ler .SRT
        subtitles = self._read_srt(srt_file)
        
        # Escrever .ASS
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("[Script Info]\n")
            f.write("Title: Generated by AI-Shorts-Generator\n")
            f.write("ScriptType: v4.00+\n\n")
            
            # Estilos
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, Bold, Outline\n")
            f.write(f"Style: Default,Arial,{selected_style['fontsize']},{selected_style['primarycolour']},{selected_style['bold']},{selected_style['outline']}\n\n")
            
            # Eventos
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Text\n")
            
            for sub in subtitles:
                start = self._format_ass_time(sub['start'])
                end = self._format_ass_time(sub['end'])
                text = sub['text'].replace('\n', '\\N')
                
                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")
        
        print(f"   ✅ Estilo .ASS gerado: {style}")
        
        return output_file
    
    def _read_srt(self, srt_file):
        """Lê arquivo .SRT."""
        subtitles = []
        
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Dividir em blocos
        blocks = re.split(r'\n\n+', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            # Parsear timestamps
            timestamp_line = lines[1]
            match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})', timestamp_line)
            
            if match:
                h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
                
                start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
                end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000
                
                text = '\n'.join(lines[2:])
                
                subtitles.append({
                    'start': start,
                    'end': end,
                    'text': text
                })
        
        return subtitles
    
    def _format_ass_time(self, seconds):
        """Formata timestamp para .ASS (H:MM:SS.cc)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centis = int((seconds % 1) * 100)
        
        return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def generate_subtitles_for_short(transcription_segments, short_path):
    """
    Gera legendas para um short.
    
    Args:
        transcription_segments: Segmentos da transcrição
        short_path: Caminho do short (.mp4)
    
    Returns:
        Tupla (srt_path, ass_path)
    """
    generator = SubtitleGenerator()
    
    # Gerar .SRT
    srt_path = str(Path(short_path).with_suffix('.srt'))
    generator.generate_srt(transcription_segments, srt_path)
    
    # Gerar .ASS (estilo padrão)
    ass_path = generator.generate_ass(srt_path, style='default')
    
    return srt_path, ass_path
