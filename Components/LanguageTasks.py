# Components/LanguageTasks.py
"""
=============================================================================
IDENTIFICAÇÃO DE HIGHLIGHTS COM GPT - VERSÃO ATUAL
=============================================================================

⚠️ PROBLEMAS CONHECIDOS:
1. GPT retorna clips muito curtos (2-5s) mesmo com instruções explícitas
2. Prompt não é consistente - às vezes funciona, às vezes não
3. Limite de tokens (120k) impede análise de lives muito longas (5h+)
4. GPT não entende bem o conceito de "contexto completo"
5. Temperature 0.3 pode estar tornando respostas muito mecânicas

✅ O QUE FUNCIONA:
- Detecção de marcadores [RISO] na transcrição
- Expansão forçada ao redor do clímax
- Fallback para formato antigo (setup_start/reaction_end)

🔧 MELHORIAS NECESSÁRIAS:
1. Usar few-shot learning (exemplos reais no prompt)
2. Dividir live em chunks menores (processar 30min por vez)
3. Implementar validação de duração ANTES de retornar
4. Adicionar lógica de retry se clips forem muito curtos
5. Considerar usar modelo diferente (GPT-4 ou Claude)
6. Criar prompt mais simples: "encontre timestamps de momentos engraçados"
   e deixar a expansão 100% pro Python

🎯 SOLUÇÃO IDEAL FUTURA:
- Analisar áudio diretamente (picos de volume = risadas)
- Usar ML para detectar padrões de risada no waveform
- Combinar análise de áudio + transcrição
- Sistema de scoring baseado em múltiplos fatores

=============================================================================
"""

import os
import json
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API"):
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API")
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️ OPENAI_API_KEY não encontrada no .env")


def _clean_llm_json(raw: str) -> str:
    """
    Remove markdown ```json do retorno do LLM.
    
    PROBLEMA: GPT às vezes retorna com ```json e às vezes sem
    SOLUÇÃO: Regex para limpar ambos os casos
    """
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
        raw = re.sub(r"```$", "", raw).strip()
    return raw


def GetHighlights(transcript_text: str, video_duration_min: float = 240):
    """
    Retorna highlights com DURAÇÃO FORÇADA de 45-180s.
    
    FLUXO ATUAL:
    1. Envia prompt pro GPT pedindo "clímax" de momentos
    2. GPT retorna lista de timestamps
    3. Python expande ao redor do clímax (40% antes, 60% depois)
    
    ⚠️ PROBLEMA: GPT às vezes retorna mesmo timestamp repetido (climax: 44.0, 44.0, 44.0...)
    ⚠️ PROBLEMA: Não há garantia que o "clímax" está correto
    
    🔧 MELHORIA NECESSÁRIA:
    - Validar que timestamps são diferentes
    - Adicionar margem de erro (se muitos clips no mesmo segundo, distribuir)
    - Implementar retry lógico se resposta for ruim
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # CONSIDERAÇÃO: Testar gpt-4-turbo-preview
        temperature=0.3  # CONSIDERAÇÃO: Testar 0.5-0.7 para mais variação
    )

    # CÁLCULO DE MOMENTOS: 5h = 300min → 300/4 = 75 momentos
    # PROBLEMA: Pedir muitos momentos pode resultar em qualidade baixa
    # MELHORIA: Pedir menos (20-30) mas com critério mais rigoroso
    num_moments = min(60, max(30, int(video_duration_min / 4)))

    prompt = ChatPromptTemplate.from_template(
        """
Você é editor de Shorts VIRAIS de GAMES.

ENCONTRE momentos com RISADAS, FAILS, CLUTCHES, RAGE.

Procure na transcrição por:
- "KKKK", "hahaha", "[RISO]"  # <- Marcadores adicionados pelo Transcription.py
- "caralho!", "porra!", "mano!"
- "NÃOOO!", "CONSEGUI!", "WTF"

Para cada momento, retorne o timestamp do CLÍMAX.

JSON:
[
  {{"climax": 380.5, "reason": "rizada + fail"}},
  {{"climax": 1250.0, "reason": "clutch épico"}}
]

Retorne {num_moments} momentos.

TRANSCRIÇÃO:
{transcript}
"""
    )
    # PROBLEMA DO PROMPT:
    # 1. Muito genérico - não dá exemplos concretos
    # 2. Não explica o que é "clímax" claramente
    # 3. Não penaliza repetições
    # 
    # MELHORIA SUGERIDA:
    # - Adicionar 3-5 exemplos reais (few-shot)
    # - Especificar: "climax = momento exato da risada/reação"
    # - Adicionar: "NUNCA repita o mesmo timestamp"

    chain = prompt | llm
    response = chain.invoke({
        "transcript": transcript_text[:120000],  # LIMITAÇÃO: 120k tokens = ~2-3h de live
        "num_moments": num_moments
    })
    # PROBLEMA: Live de 5h não cabe em 120k tokens
    # SOLUÇÃO FUTURA: Dividir em chunks de 30min, processar separadamente

    raw = response.content
    print(f"🔍 DEBUG - Resposta do GPT (primeiros 500 chars):")
    print(raw[:500])
    # MANTER ESSE DEBUG - útil para diagnosticar problemas
    
    cleaned = _clean_llm_json(raw)

    try:
        moments = json.loads(cleaned)
    except Exception as e:
        print(f"❌ Erro ao parsear JSON: {e}")
        print(f"Raw: {raw[:500]}")
        return []
        # MELHORIA: Implementar retry com prompt simplificado se JSON falhar

    # PÓS-PROCESSAMENTO: FORÇAR DURAÇÕES CORRETAS
    valid_clips = []
    seen_timestamps = set()  # ADICIONAR: Evitar duplicatas
    
    for m in moments:
        try:
            # Pegar o clímax (ou usar setup_start se for o formato antigo)
            if "climax" in m:
                climax = float(m["climax"])
            elif "punchline" in m:
                climax = float(m["punchline"])
            else:
                continue
            
            # VERIFICAR DUPLICATAS
            # PROBLEMA: GPT às vezes retorna climax: 44.0 repetido 50x
            if climax in seen_timestamps:
                continue  # Pular duplicatas
            seen_timestamps.add(climax)
            
            # FORÇAR duração 45-180s ao redor do clímax
            duration = 60  # Duração padrão
            
            # AJUSTE DINÂMICO baseado no motivo
            # CONSIDERAÇÃO: Isso pode não ser ideal - testar durações fixas
            reason = m.get("reason", "").lower()
            if "clutch" in reason or "épico" in reason:
                duration = 90  # Clutches precisam de mais contexto
            elif "riso" in reason or "kkkk" in reason:
                duration = 60  # Risadas são mais curtas
            elif "fail" in reason:
                duration = 75
            
            # Calcular start e end ao redor do clímax
            # 40% antes (setup) + 60% depois (reação)
            start = max(0, climax - (duration * 0.4))
            end = climax + (duration * 0.6)
            
            # VALIDAÇÃO ADICIONAL NECESSÁRIA:
            # - Verificar se não ultrapassa duração do vídeo
            # - Garantir que start < end (óbvio mas importante)
            # - Verificar se há palavras suficientes nesse intervalo
            
            valid_clips.append({
                "start": start,
                "end": end,
                "reason": m.get("reason", ""),
                "score": 1.0  # FUTURO: Calcular score real baseado em múltiplos fatores
            })
            
        except (KeyError, ValueError, TypeError) as e:
            continue

    print(f"✅ {len(valid_clips)} highlights encontrados (expansão forçada aplicada)")
    
    # ORDENAR POR TIMESTAMP para facilitar deduplicação posterior
    valid_clips = sorted(valid_clips, key=lambda x: x["start"])
    
    return valid_clips

# PRÓXIMOS PASSOS SUGERIDOS:
# 1. Implementar análise de áudio direto (sem GPT)
# 2. Criar sistema de scoring por múltiplos fatores
# 3. Adicionar cache de resultados (não processar mesma live 2x)
# 4. Implementar sistema de feedback (aprender com shorts aprovados)
# 5. Considerar usar modelo local (Whisper local + análise de áudio)
