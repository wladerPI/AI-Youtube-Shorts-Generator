# AI YouTube Shorts Generator — Visão Geral do Projeto

> **Documento para contexto:** Este arquivo existe para que a IA (Cursor) e desenvolvedores entendam rapidamente o projeto ao retomá-lo. Leia este arquivo ANTES de qualquer alteração.

---

## O QUE É ESTE PROJETO

Sistema em Python que transforma **lives longas** (4–6 horas) de canal de **Games e Humor** em múltiplos **YouTube Shorts** prontos para publicação. O objetivo é automatizar a criação de cortes virais para redes sociais (YouTube Shorts, TikTok, Reels).

**Canal alvo:** Games + Humor, com uso frequente de memes que aparecem nos cantos da tela.

---

## FLUXO DO PIPELINE

```
1. Vídeo de entrada (live)
2. Extração de áudio (WAV)
3. Transcrição com Whisper (palavra por palavra, com timestamps)
4. Seleção de segmentos via LLM (GPT) — rizadas, memes, rage, humor
5. Merge de blocos coerentes (não corta frases no meio)
6. Deduplicação (evita segmentos sobrepostos ou repetidos)
7. Para cada segmento:
   - Corte do vídeo (start → end)
   - Remoção de silêncios longos
   - Render vertical 9:16 COM ÁUDIO
   - Pan da câmera quando memes/faces aparecem nos cantos
   - Legendas SRT
8. ranking.json com scores (viral, retention, rank)
```

---

## COMO EXECUTAR

```cmd
python run_pipeline.py input\video.mp4
```

Ou via `run.bat` (Windows) ou `run.sh` (Linux).

**Requisito:** Arquivo `.env` com `OPENAI_API_KEY` para seleção por LLM. Sem a chave, usa fallback heurístico.

---

## ESTRUTURA DOS ARQUIVOS

| Arquivo | Função |
|---------|--------|
| `run_pipeline.py` | Ponto de entrada; orquestra todo o pipeline |
| `Config.py` | Constantes (resolução, pan, thresholds) |
| `PipelineConfig.py` | Modos TEST / LIVE / INSANO (quantidade de shorts) |
| `Components/Edit.py` | Extração de áudio e corte de vídeo |
| `Components/Transcription.py` | Whisper (transcrição com timestamps) |
| `Components/SegmentSelectorLLM.py` | Seleção via GPT + merge coerente |
| `Components/AISegmentSelector.py` | Fallback heurístico (sem LLM) |
| `Components/LanguageTasks.py` | GetHighlights — prompt para GPT |
| `Components/EtapaG_CoherentSegments.py` | Expande highlights para blocos coerentes |
| `Components/EtapaJ_RemoveSilence.py` | Remove silêncios longos |
| `Components/MemeCornerDetector.py` | Detecta faces/memes nos cantos (pan) |
| `Render/VerticalCropper.py` | Render vertical 9:16 com MoviePy (preserva áudio) |
| `Components/SubtitleGenerator.py` | Legendas SRT (agrupadas em frases) |

---

## ALTERAÇÕES REALIZADAS (Resumo)

1. **Áudio nos shorts:** VerticalCropper reescrito com MoviePy (antes perdia áudio com OpenCV).
2. **Pan para memes:** MemeCornerDetector detecta faces nos cantos; câmera faz pan.
3. **Seleção por LLM:** Uso de GPT para rizadas, memes, rage (antes só heurística).
4. **Contexto completo:** merge_coherent_segments evita cortes no meio de frases.
5. **Deduplicação:** Evita segmentos sobrepostos (ex.: Clip 1 e 5 eram iguais).
6. **Duração flexível:** Shorts de 30s a 3min (ajuste final no CapCut).
7. **Mais shorts por live:** LIVE=25, INSANO=35 (antes 10 e 25).

---

## O QUE AINDA PODE SER FEITO

- **Melhorar detecção de memes:** Usar detecção de objetos (YOLO) além de faces.
- **Detecção de risada no áudio:** Usar análise de frequência para picos de risada.
- **Legendagem em karaoke:** Palavras destacando em tempo real.
- **Priorização por histórico:** Aprender com shorts que viralizaram.
- **Batch de múltiplos vídeos:** Processar várias lives de uma vez.
- **Integração CapCut:** API ou export automático para edição.
- **Whisper em GPU:** Usar CUDA se disponível para transcrição mais rápida.

---

## NOTAS PARA A IA

- O usuário faz retoques no CapCut; os shorts não precisam estar perfeitos.
- Lives têm ~4–6 horas; o foco é em muitos bons cortes, não poucos perfeitos.
- Memes costumam aparecer nos cantos da tela; o pan deve focar neles por alguns segundos.
- A maior parte do tempo a tela deve ficar centralizada.
- Manter contexto narrativo é prioridade (não cortar frases no meio).
