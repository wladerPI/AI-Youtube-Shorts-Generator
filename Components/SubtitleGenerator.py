# Components/SubtitleGenerator.py
"""
=============================================================================
GERAÇÃO DE LEGENDAS SRT
=============================================================================

O QUE FAZ:
  Gera arquivo SRT a partir da transcrição e dos limites do clip.
  Por padrão agrupa palavras em frases curtas (3-6 palavras ou ~2s) para
  legibilidade em shorts.

POR QUE AGRUPAR:
  Legenda palavra-por-palavra fica muito fragmentada. Agrupar em frases
  é mais natural para leitura. O usuário pode ajustar no CapCut.

ALTERAÇÕES:
  - group_phrases=True por padrão (antes era palavra-por-palavra)
  - MAX_WORDS=5, MAX_DURATION=2.2 para blocos legíveis

O QUE AINDA PODE SER FEITO:
  - Estilo karaoke (destacar palavra atual)
  - Máximo de caracteres por linha (padrão broadcast)
  - Export em ASS para estilização avançada
=============================================================================
"""

def format_time(seconds):
    """Formato SRT: HH:MM:SS,mmm"""
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds) % 60
    m = int(seconds // 60)
    h = int(seconds // 3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def generate_srt(transcriptions, clip_start, clip_end, output_path, group_phrases=True):
    """
    group_phrases=True: agrupa 3-6 palavras por legenda (mais legível)
    group_phrases=False: uma palavra por legenda (estilo karaoke)
    """
    in_range = [
        (w, s, e) for w, s, e in transcriptions
        if e > clip_start and s < clip_end
    ]
    if not in_range:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("")
        return

    entries = []
    idx = 1

    if group_phrases:
        MAX_WORDS = 5
        MAX_DURATION = 2.2
        phrase_words = []
        phrase_start = None

        for word, start, end in in_range:
            s = max(start, clip_start) - clip_start
            e = min(end, clip_end) - clip_start
            if phrase_start is None:
                phrase_start = s
            phrase_words.append((word, s, e))

            duration = e - phrase_start
            if len(phrase_words) >= MAX_WORDS or duration >= MAX_DURATION:
                text = " ".join(w for w, _, _ in phrase_words)
                entries.append(
                    f"{idx}\n"
                    f"{format_time(phrase_start)} --> {format_time(e)}\n"
                    f"{text}\n"
                )
                idx += 1
                phrase_words = []
                phrase_start = None

        if phrase_words:
            text = " ".join(w for w, _, _ in phrase_words)
            _, _, e = phrase_words[-1]
            entries.append(
                f"{idx}\n"
                f"{format_time(phrase_start)} --> {format_time(e)}\n"
                f"{text}\n"
            )
    else:
        for word, start, end in in_range:
            s = max(start, clip_start) - clip_start
            e = min(end, clip_end) - clip_start
            if e - s < 0.05:
                continue
            entries.append(
                f"{idx}\n"
                f"{format_time(s)} --> {format_time(e)}\n"
                f"{word}\n"
            )
            idx += 1

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(entries))

    print(f"✅ SRT criado: {output_path}")
