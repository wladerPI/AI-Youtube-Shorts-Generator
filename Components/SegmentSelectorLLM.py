# Components/SegmentSelectorLLM.py
"""
=============================================================================
SELETOR DE SEGMENTOS COM LLM (GPT)
=============================================================================

⚠️ PROBLEMA IDENTIFICADO:
Esta é a camada que MATA a maioria dos clips!

FLUXO ATUAL:
1. LanguageTasks.py retorna 84 clips com duração forçada (45-180s) ✅
2. Este arquivo chama merge_coherent_segments() 
3. merge_coherent_segments REJEITA quase todos ❌
4. Resultado: 84 clips → 0 clips finais

POR QUE merge_coherent_segments REJEITA?
- Tenta "expandir" clips para incluir contexto completo
- Mas LanguageTasks.py já fez isso!
- Acaba duplicando lógica e criando conflitos
- Parâmetros (gap_tolerance, context_padding) muito restritivos

🔧 SOLUÇÃO IMPLEMENTADA (temporária):
- Bypass do merge_coherent_segments
- Usa clips direto do LanguageTasks.py
- Filtro simples por duração

⚠️ PROBLEMA DESSA SOLUÇÃO:
- Perde validação de contexto
- Pode gerar clips que cortam frases no meio

✅ SOLUÇÃO IDEAL (futuro):
- Remover merge_coherent_segments completamente
- Mover toda lógica de contexto para LanguageTasks.py
- OU criar novo componente simples de validação
- Usar análise de transcrição para garantir frases completas

=============================================================================
"""

import json
import os
from dotenv import load_dotenv
load_dotenv()

from Components.LanguageTasks import GetHighlights


def _build_transcript_with_timestamps(transcriptions, interval_sec=15):
    """
    Converte transcrição em texto com timestamps [MM:SS].
    
    FUNCIONA BEM - Não precisa de alterações.
    
    FORMATO DE SAÍDA:
    [0:00] palavra palavra palavra
    [0:15] palavra palavra palavra
    [0:30] palavra palavra palavra
    
    NOTA: interval_sec=15 significa agrupar palavras a cada 15s
    CONSIDERAÇÃO: Testar com 10s ou 20s para ver impacto
    """
    if not transcriptions:
        return ""

    lines = []
    current_time = 0
    current_words = []

    for word, start, end in transcriptions:
        if start >= current_time + interval_sec and current_words:
            ts = int(current_time)
            lines.append(f"[{ts//60}:{ts%60:02d}] {' '.join(current_words)}")
            current_time = int(start / interval_sec) * interval_sec
            current_words = []
        current_words.append(word)

    if current_words:
        ts = int(current_time)
        lines.append(f"[{ts//60}:{ts%60:02d}] {' '.join(current_words)}")

    return "\n".join(lines)


def select_segments_with_llm(
    transcriptions,
    max_segments=25,
    min_duration=30,
    max_duration=180,
    prefer_llm=True,
    video_duration_min=240
):
    """
    FUNÇÃO PRINCIPAL - SELEÇÃO DE SEGMENTOS
    
    VERSÃO ATUAL (simplificada):
    1. Chama GetHighlights (retorna clips já expandidos)
    2. Filtra por duração
    3. Retorna direto (sem merge_coherent_segments)
    
    ⚠️ PROBLEMA: Muito simplista
    ⚠️ PROBLEMA: Não valida qualidade dos clips
    
    🔧 MELHORIAS NECESSÁRIAS:
    1. Validar que clips têm palavras suficientes
    2. Verificar que não cortam frases no meio
    3. Calcular score de qualidade (contexto, densidade de palavras, etc)
    4. Ordenar por score antes de retornar
    5. Adicionar deduplicação inteligente (não só por gap temporal)
    
    PARÂMETROS:
    - max_segments: Máximo de clips a retornar
    - min_duration: Duração mínima em segundos (padrão: 30s)
    - max_duration: Duração máxima em segundos (padrão: 180s)
    - prefer_llm: Se True, usa GPT. Se False, usa heurística
    - video_duration_min: Duração total do vídeo (para cálculo de quantos clips pedir)
    
    RETORNO:
    Lista de dicts: [{"start": 100.0, "end": 160.0, "reason": "fail épico", "score": 1.0}, ...]
    """
    transcript_text = _build_transcript_with_timestamps(transcriptions, interval_sec=20)

    if not transcript_text.strip():
        return []

    if prefer_llm and (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API")):
        try:
            # CHAMADA PRINCIPAL: GetHighlights
            highlights = GetHighlights(transcript_text, video_duration_min=video_duration_min)
            
            if not highlights:
                print("⚠️ GetHighlights retornou 0 clips")
                # Fallback para método heurístico (sem GPT)
                return _fallback_heuristic(transcriptions, max_segments, min_duration, max_duration)
            
            # BYPASS DO merge_coherent_segments (estava rejeitando tudo)
            print(f"✅ Usando {len(highlights)} clips direto do GPT")
            
            # Filtro simples por duração
            valid_segments = []
            for h in highlights:
                duration = h["end"] - h["start"]
                
                # Validação básica
                if min_duration <= duration <= max_duration:
                    valid_segments.append(h)
                else:
                    # LOG: Por que foi rejeitado
                    # MELHORIA: Salvar isso em arquivo de log
                    if duration < min_duration:
                        pass  # Muito curto
                    else:
                        pass  # Muito longo
            
            print(f"✅ {len(valid_segments)} clips passaram no filtro de duração")
            
            # MELHORIA FUTURA: Ordenar por score antes de limitar
            # valid_segments = sorted(valid_segments, key=lambda x: x.get("score", 0), reverse=True)
            
            # Limitar ao máximo solicitado
            return valid_segments[:max_segments]
            
        except Exception as e:
            print(f"⚠️ LLM falhou ({e}) — usando fallback heurístico")
            # Em caso de erro, usar método heurístico

    return _fallback_heuristic(transcriptions, max_segments, min_duration, max_duration)


def _fallback_heuristic(transcriptions, max_seg, min_dur, max_dur):
    """
    Método heurístico (sem GPT) para seleção de clips.
    
    QUANDO É USADO:
    - Quando prefer_llm=False
    - Quando não há OPENAI_API_KEY
    - Quando GPT falha/crasheia
    
    COMO FUNCIONA:
    - Usa AISegmentSelector (baseado em palavras-chave)
    - Busca por densidade de palavras interessantes
    - Não usa IA, apenas regex e contagem
    
    ⚠️ PROBLEMA: Muito menos preciso que GPT
    ⚠️ PROBLEMA: Não detecta contexto ou humor
    
    ✅ VANTAGEM: Rápido, gratuito, sempre funciona
    
    CONSIDERAÇÃO: Melhorar heurística com:
    - Análise de picos de áudio
    - Detecção de mudanças de tom
    - Contagem de marcadores [RISO]
    """
    try:
        from Components.AISegmentSelector import select_best_segments
        
        # NOTA: mode="RELAXED" aceita mais clips
        # Outros modos: "STRICT", "BALANCED"
        raw = select_best_segments(transcriptions, mode="RELAXED")
        
        # Filtrar por duração e limitar quantidade
        filtered = [
            {"start": s["start"], "end": s["end"], "reason": s.get("reason", "")}
            for s in raw[:max_seg * 2]  # Pega o dobro e filtra
            if min_dur <= (s["end"] - s["start"]) <= max_dur
        ][:max_seg]  # Limita ao máximo
        
        return filtered
        
    except Exception as e:
        print(f"⚠️ Fallback também falhou: {e}")
        return []


# =============================================================================
# PRÓXIMOS PASSOS E MELHORIAS
# =============================================================================

"""
🔴 CRÍTICO (fazer primeiro):
1. Decidir: merge_coherent_segments fica ou sai?
   - Se fica: Consertar parâmetros
   - Se sai: Melhorar validação aqui

2. Implementar logging detalhado:
   - Quantos clips foram rejeitados em cada etapa
   - Por que foram rejeitados (muito curto, muito longo, etc)
   - Salvar em arquivo log/selection_{session}.txt

3. Adicionar validação de qualidade:
   - Verificar densidade de palavras
   - Checar se corta frase no meio
   - Calcular score baseado em múltiplos fatores

🟡 IMPORTANTE (próxima iteração):
1. Ordenação inteligente por score
2. Deduplicação baseada em conteúdo (não só tempo)
3. Distribuição uniforme ao longo da live
4. Priorizar primeiros 30min (hook melhor)

🟢 DESEJÁVEL (longo prazo):
1. Sistema de cache (não reprocessar mesma live)
2. Integração com sistema de feedback
3. ML para aprender preferências
4. A/B testing de diferentes estratégias

DÚVIDAS A RESOLVER:
- merge_coherent_segments é realmente necessário?
- Devemos confiar 100% no GPT ou adicionar validação?
- Como balancear quantidade vs qualidade?
- Vale a pena implementar heurística melhor ou focar no GPT?
"""
