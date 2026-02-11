# Components/LanguageTasks.py
"""
=============================================================================
IDENTIFICAÇÃO DE HIGHLIGHTS COM GPT
=============================================================================

O QUE FAZ:
  Chama GPT-4o-mini para analisar a transcrição e retornar os melhores
  momentos em JSON: setup_start, punchline, reaction_end, reason.
  Prioridade: RIZADAS > memes > rage > reações > humor.

POR QUE RIZADAS PRIMEIRO:
  O canal é de Games e Humor; momentos de risada são os mais virais.

ALTERAÇÕES:
  - Duração expandida: 30s a 3min (antes 6-60s)
  - num_moments dinâmico: 12-25 conforme duração do vídeo
  - Suporte a OPENAI_API além de OPENAI_API_KEY

O QUE AINDA PODE SER FEITO:
  - Prompt em few-shot com exemplos reais
  - Análise de tom (detectar risada na transcrição)
  - Múltiplas chamadas para vídeos muito longos (evitar token limit)
=============================================================================
"""

import os
import json
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Suportar .env com OPENAI_API ou OPENAI_API_KEY
if not os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API"):
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API")
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️ OPENAI_API_KEY não encontrada no .env — seleção por LLM desativada")


def _clean_llm_json(raw: str) -> str:
    """Remove markdown ```json do retorno do LLM."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
        raw = re.sub(r"```$", "", raw).strip()
    return raw


def GetHighlights(transcript_text: str, video_duration_min: float = 240):
    """
    Retorna lista de highlights: [{"start", "end", "reason"}, ...]
    transcript_text deve ter timestamps no formato [MM:SS] texto.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.4
    )

    # Quantos momentos pedir: ~1 a cada 15 min de vídeo, entre 12 e 25
    num_moments = min(25, max(12, int(video_duration_min / 15)))

    prompt = ChatPromptTemplate.from_template(
        """
Você é um editor PROFISSIONAL de Shorts virais para canal de GAMES e HUMOR.

Analise a transcrição (com timestamps [MM:SS]) e encontre os MELHORES MOMENTOS para shorts.

PRIORIDADE MÁXIMA:
1. RIZADAS — momentos em que você ou alguém RI MUITO (principal foco!)
2. MEMES — quando um meme aparece ou é mencionado
3. RAGE — gritos, xingamentos, frustração engraçada
4. REAÇÕES EXAGERADAS — sustos, surpresas, "não acredito"
5. HUMOR — punchlines, piadas que funcionam sozinhas

REGRAS OBRIGATÓRIAS:
- Cada momento deve ter CONTEXTO COMPLETO (nunca cortar frase no meio)
- O trecho deve fazer sentido sozinho (espectador entrando no meio)
- Duração: ENTRE 30 SEGUNDOS E 3 MINUTOS por momento
- Retorne entre {num_moments} e {num_moments} momentos (use o total de timestamps como guia)
- Use os timestamps [MM:SS] para indicar setup_start e reaction_end com precisão
- Evite silêncios longos no meio do momento

FORMATO JSON (sem texto extra):
[
  {{
    "setup_start": 380.2,
    "punchline": 399.6,
    "reaction_end": 412.9,
    "reason": "rizada forte com meme"
  }}
]

TRANSCRIÇÃO:
{transcript}
"""
    )

    chain = prompt | llm
    response = chain.invoke({
        "transcript": transcript_text[:120000],  # Limite de tokens
        "num_moments": num_moments
    })

    raw = response.content
    cleaned = _clean_llm_json(raw)

    try:
        moments = json.loads(cleaned)
    except Exception as e:
        print(f"❌ Erro ao parsear JSON da IA: {e}")
        return []

    valid_clips = []
    MIN_LENGTH = 30
    MAX_LENGTH = 180

    for m in moments:
        try:
            raw_start = float(m["setup_start"])
            start = max(0, raw_start - 2)  # 2s de contexto extra
            end = float(m["reaction_end"])
            duration = end - start

            if MIN_LENGTH <= duration <= MAX_LENGTH:
                valid_clips.append({"start": start, "end": end, "reason": m.get("reason", "")})
            elif duration < MIN_LENGTH and duration >= 15:
                # Aceita trechos curtos mas com contexto
                valid_clips.append({"start": start, "end": end, "reason": m.get("reason", "")})
        except (KeyError, ValueError, TypeError):
            continue

    print(f"✅ {len(valid_clips)} highlights encontrados pela IA")
    return valid_clips
