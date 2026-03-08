# 🎯 ANÁLISE COMPLETA E ROADMAP DE MELHORIAS
# AI-Youtube-Shorts-Generator - Projeto 11closed
# Data: 2026-02-15

"""
=============================================================================
VISÃO GERAL DO PROJETO
=============================================================================

OBJETIVO PRINCIPAL:
Criar shorts inteligentes (15s-3min) de lives de gameplay SEM WEBCAM,
focando em:
- 🎭 MEMES (visuais nos cantos da tela)
- 😂 RIZADAS (detectadas no áudio)
- 🎮 MOMENTOS LEGAIS (fails, clutches, explicações)
- 📝 LEGENDAS COMPLETAS em PT-BR (gírias, memes, tudo)

CARACTERÍSTICAS ESPECÍFICAS DAS SUAS LIVES:
- Gameplay puro (sem webcam)
- Memes aparecem nos CANTOS da tela
- Memes ficam 3-6 segundos e somem
- Humor + gameplay + comentários
- Memes recorrentes entre lives

WORKFLOW IDEAL:
1. Detectar momentos engraçados (áudio + transcrição)
2. Cortar com contexto COMPLETO
3. Remover silêncios longos (>3s)
4. Câmera inteligente: CENTRO → MEME (cantos) → CENTRO
5. Legendas 100% completas
6. Sistema aprende suas preferências

=============================================================================
"""

# =============================================================================
# PARTE 1: PROBLEMAS CRÍTICOS ATUAIS
# =============================================================================

PROBLEMA_1_FILTROS_AGRESSIVOS = """
ARQUIVO: run_pipeline.py (linhas 113-120)
PROBLEMA: 
- Gera 500+ clips → filtros matam 540 → restam 4 shorts
- min_gap=60s muito restritivo
- filter_by_time_distance redundante

SOLUÇÃO IMEDIATA:
```python
# ANTES (linha 113):
segments = _deduplicate_segments(segments, min_gap=60)

# DEPOIS:
segments = _deduplicate_segments(segments, min_gap=15)  # 15s é suficiente
```

SOLUÇÃO IDEAL:
- Remover deduplicação por tempo
- Deduplic por CONTEÚDO (comparar transcrição)
- Permitir múltiplos shorts próximos se forem momentos diferentes
"""

PROBLEMA_2_GPT_INCONSISTENTE = """
ARQUIVO: Components/LanguageTasks.py
PROBLEMA:
- GPT retorna clips de 2s às vezes, 60s outras vezes
- Não entende "contexto completo"
- Prompt muito genérico

SOLUÇÃO IMEDIATA:
- Expansão forçada em Python (JÁ IMPLEMENTADO)
- Validar duração ANTES de retornar

SOLUÇÃO IDEAL:
- Few-shot learning (3-5 exemplos reais no prompt)
- OU análise de áudio direta (picos = risadas)
- OU combinar GPT + análise de áudio
"""

PROBLEMA_3_SEM_DETECCAO_VISUAL_DE_MEMES = """
ARQUIVOS AFETADOS: Todos
PROBLEMA CRÍTICO:
- Sistema só analisa ÁUDIO/TRANSCRIÇÃO
- MEMES VISUAIS não são detectados
- Câmera não sabe quando meme aparece nos cantos

IMPACTO:
- Shorts perdem contexto visual
- Movimento de câmera não foca memes
- Não aproveita o melhor das suas lives

SOLUÇÃO NECESSÁRIA:
Criar novo módulo: Components/MemeDetector.py
- Detectar mudanças nos cantos da tela (canto superior/inferior esquerdo/direito)
- Usar template matching para memes recorrentes
- OCR para texto de memes
- Salvar "biblioteca de memes" no perfil
"""

PROBLEMA_4_LEGENDAS_INCOMPLETAS = """
ARQUIVO: Components/SubtitleGenerator.py
PROBLEMA:
- Algumas palavras somem
- Gírias/risadas não são transcritas corretamente
- Textos de memes não aparecem

SOLUÇÃO:
- Melhorar agrupamento (atual: 5 palavras/5s)
- Post-processar transcrição: adicionar gírias comuns
- Detectar texto em memes (OCR) e adicionar como legenda especial
"""

PROBLEMA_5_SISTEMA_DE_PERFIL_NAO_INTEGRADO = """
ARQUIVOS: profile_learning.py, review_shorts.py
PROBLEMA:
- Criados mas não usados no pipeline
- Não há feedback loop

SOLUÇÃO:
- Integrar review_shorts.py após geração
- Usar profile.json para ajustar seleção
- Sistema deve aprender:
  * Memes recorrentes
  * Frases favoritas
  * Durações ideais
  * Tipos de momento (fail > clutch > explicação)
"""

# =============================================================================
# PARTE 2: ARQUITETURA IDEAL FUTURA
# =============================================================================

ARQUITETURA_NOVA = """
┌─────────────────────────────────────────────────────────────┐
│                    INPUT: live.mp4 (5h)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ETAPA 1: ANÁLISE MULTI-MODAL                                │
│ ├─ Whisper (transcrição PT-BR)                              │
│ ├─ Análise de áudio (picos = risadas)                       │
│ ├─ MemeDetector (detecta memes visuais nos cantos)          │
│ └─ OCR em memes (extrai texto)                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ETAPA 2: SELEÇÃO INTELIGENTE                                │
│ ├─ GPT (analisa transcrição + picos de áudio)               │
│ ├─ Carrega perfil lives_do_11closed                         │
│ ├─ Prioriza: memes recorrentes + rizadas + seus padrões     │
│ └─ Retorna 50+ candidatos com score                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ETAPA 3: EXPANSÃO DE CONTEXTO                               │
│ ├─ Garante 15s-3min por clip                                │
│ ├─ Não corta frases no meio                                 │
│ ├─ Inclui setup + punchline + reação                        │
│ └─ Valida densidade de palavras                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ETAPA 4: RENDERIZAÇÃO INTELIGENTE                           │
│ ├─ Remove silêncios >3s (mas não corta frases)              │
│ ├─ Câmera: CENTRO → MEME (3-6s) → CENTRO                    │
│ ├─ Usa coordenadas de MemeDetector                          │
│ ├─ Legendas COMPLETAS (+ texto de memes)                    │
│ └─ 30-40 shorts prontos                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ETAPA 5: REVISÃO E APRENDIZADO                              │
│ ├─ review_shorts.py (você aprova/rejeita)                   │
│ ├─ Sistema aprende preferências                             │
│ ├─ Atualiza perfil lives_do_11closed                        │
│ └─ Próxima live: seleção 20% melhor                         │
└─────────────────────────────────────────────────────────────┘
"""

# =============================================================================
# PARTE 3: NOVOS MÓDULOS NECESSÁRIOS
# =============================================================================

MODULO_1_MEME_DETECTOR = """
ARQUIVO A CRIAR: Components/MemeDetector.py

OBJETIVO:
Detectar quando memes aparecem nos CANTOS da tela (suas lives)

COMO FUNCIONA:
1. Divide tela em regiões: Centro, TopLeft, TopRight, BottomLeft, BottomRight
2. Detecta mudanças significativas nos cantos
3. Extrai frame do meme
4. Faz OCR do texto (se tiver)
5. Compara com biblioteca de memes conhecidos
6. Retorna timestamps + posição + texto

OUTPUT:
{
  "timestamp": 125.5,
  "position": "top_right",
  "text": "KKKK ELE MORREU",
  "meme_id": "risada_classica_1",
  "duration": 4.2
}

INTEGRAÇÃO:
- Chamar durante Transcription (em paralelo com Whisper)
- Salvar eventos de memes em meme_events.json
- Usar em VerticalCropper para mover câmera
- Adicionar texto do meme nas legendas

TECNOLOGIAS:
- OpenCV para detecção de mudança
- pytesseract para OCR
- Template matching para memes recorrentes
- Histograma de cores para detectar aparição/sumiço
"""

MODULO_2_PERFIL_MANAGER = """
ARQUIVO A CRIAR: Components/ProfileManager.py

OBJETIVO:
Gerenciar perfil "lives_do_11closed" com aprendizado contínuo

ESTRUTURA DO PERFIL:
{
  "channel_id": "lives_do_11closed",
  "total_lives_processed": 15,
  "total_shorts_reviewed": 450,
  "approval_rate": 0.67,
  
  "meme_library": {
    "risada_classica_1": {
      "text": "KKKK ELE MORREU",
      "frequency": 87,
      "approval_rate": 0.92,
      "typical_position": "top_right"
    },
    "rage_padrao": {
      "text": "VAI TOMAR NO CU",
      "frequency": 54,
      "approval_rate": 0.78
    }
  },
  
  "favorite_keywords": [
    "KKKK", "caralho", "porra", "mano", 
    "não acredito", "olha isso", "WTF"
  ],
  
  "optimal_duration": {
    "min": 25,
    "avg": 65,
    "max": 140
  },
  
  "preferred_moment_types": {
    "fail": 0.35,
    "rizada": 0.40,
    "clutch": 0.15,
    "explicacao": 0.10
  },
  
  "gameplay_patterns": {
    "games_played": ["CS2", "Minecraft", "GTA"],
    "peak_humor_time": "21:00-23:00",
    "avg_memes_per_hour": 12
  }
}

MÉTODOS:
- load_profile() - Carrega perfil existente
- update_from_review() - Aprende com aprovação/rejeição
- get_meme_priorities() - Quais memes priorizar
- suggest_clip_adjustments() - Sugestões baseadas em histórico
- export_insights() - Relatório de padrões aprendidos
"""

MODULO_3_CAMERA_CONTROLLER = """
ARQUIVO A ATUALIZAR: Render/VerticalCropper.py

PROBLEMA ATUAL:
- Movimento baseado em detecção de rosto (não tem nas suas lives)
- Ou movimento aleatório de pan
- NÃO usa informação de memes

SOLUÇÃO:
Integrar com MemeDetector para movimento inteligente

LÓGICA NOVA:
1. Estado padrão: CENTRO (sempre)
2. Quando meme aparece no canto: 
   - Suavemente (1s) move para o canto
   - Fica focado no meme por 3-6s
   - Suavemente (1s) volta ao CENTRO
3. Se múltiplos memes simultâneos: priorizar por score
4. Nunca ficar >8s fora do centro

PSEUDOCÓDIGO:
```python
def calculate_camera_position(current_time, meme_events):
    # Verificar se há meme ativo
    active_meme = get_active_meme(current_time, meme_events)
    
    if active_meme:
        # Meme ativo - focar nele
        target = get_corner_position(active_meme.position)
        # Suavizar transição
        return smooth_transition(current_position, target, speed=1.0)
    else:
        # Sem meme - voltar ao centro
        center = (video_width / 2, video_height / 2)
        return smooth_transition(current_position, center, speed=0.8)
```

PARÂMETROS AJUSTÁVEIS:
- transition_speed: Velocidade do movimento (1s recomendado)
- focus_duration: Tempo no meme (3-6s)
- return_delay: Delay antes de voltar (0.5s)
- corner_offset: Margem dos cantos (50px)
"""

# =============================================================================
# PARTE 4: MELHORIAS NOS MÓDULOS EXISTENTES
# =============================================================================

MELHORIA_TRANSCRIPTION = """
ARQUIVO: Components/Transcription.py

O QUE JÁ FAZ:
- Whisper para transcrição PT-BR
- Detecta picos de áudio (possíveis risadas)
- Marca com [RISO]

O QUE PRECISA MELHORAR:
1. Pós-processar transcrição para adicionar gírias:
   - "kkkk" pode virar "hahahaha" no Whisper
   - Corrigir: hahahaha → KKKK
   
2. Detectar tipos de risada:
   - [RISO_FORTE] - volume muito alto
   - [RISO_LEVE] - risada contida
   - [GARGALHADA] - risada prolongada >3s

3. Integrar com MemeDetector:
   - Se meme aparece + pico de áudio = [RISO_COM_MEME]
   - Aumentar score desse momento

CÓDIGO A ADICIONAR:
```python
def post_process_transcription(words, audio_peaks, meme_events):
    '''
    Enriquece transcrição com contexto de memes e tipo de risada
    '''
    for i, (word, start, end) in enumerate(words):
        # Corrigir gírias comuns
        if word.lower() in ['hahaha', 'hahahah']:
            word = 'KKKK'
        
        # Verificar se coincide com meme
        nearby_meme = find_meme_near(start, meme_events, tolerance=2.0)
        if nearby_meme:
            word = f'[MEME:{nearby_meme.text}] {word}'
        
        # Classificar tipo de riso
        if '[RISO]' in word:
            riso_type = classify_laughter(start, audio_peaks)
            word = word.replace('[RISO]', f'[{riso_type}]')
        
        words[i] = (word, start, end)
    
    return words
```
"""

MELHORIA_SUBTITLE_GENERATOR = """
ARQUIVO: Components/SubtitleGenerator.py

PROBLEMA ATUAL:
- Agrupa 5 palavras OU 5 segundos
- Não considera pontuação natural
- Memes não aparecem nas legendas

MELHORIAS NECESSÁRIAS:

1. LEGENDAS CONSCIENTES DE CONTEXTO:
```python
def group_words_intelligently(words):
    '''
    Agrupa por frases naturais, não por contagem
    '''
    groups = []
    current_group = []
    
    for word, start, end in words:
        current_group.append(word)
        
        # Quebrar em pontuação natural
        if word.endswith(('.', '!', '?', ',')):
            groups.append(current_group)
            current_group = []
        
        # Ou se passar de 7 palavras / 6 segundos
        elif len(current_group) >= 7 or (end - groups[-1][0][1]) > 6:
            groups.append(current_group)
            current_group = []
    
    return groups
```

2. LEGENDAS DE MEMES:
- Quando meme aparece, adicionar legenda especial:
  [SUPERIOR DIREITA: "KKKK ELE MORREU"]
- Estilo diferente (cor vermelha, outline maior)
- Posição oposta ao meme (se meme tá em cima, legenda embaixo)

3. LEGENDAS DE EMOÇÃO:
- [RISO_FORTE] → 😂
- [RAGE] → 😠
- [SURPRESA] → 😱
- Emoji + texto

EXEMPLO DE OUTPUT:
```
1
00:00:25,000 --> 00:00:28,500
Olha só, vou tentar esse pulo aqui

2
00:00:28,500 --> 00:00:30,000
[😂 KKKK]
[MEME ↗️: "FAIL CLÁSSICO"]

3
00:00:30,000 --> 00:00:33,500
Não acredito que errei de novo, caralho!
```
"""

# =============================================================================
# PARTE 5: ROADMAP DE IMPLEMENTAÇÃO PRIORIZADO
# =============================================================================

ROADMAP = """
🔴 FASE 1: CORREÇÕES URGENTES (1-2 dias)
──────────────────────────────────────────
1. ✅ Reduzir min_gap de 60s para 15s
2. ✅ Comentar filter_by_time_distance (testar sem)
3. ✅ Validar durações antes de retornar clips
4. ✅ Melhorar agrupamento de legendas

RESULTADO ESPERADO: 500 clips → 30-40 shorts (não 4)

🟡 FASE 2: DETECÇÃO DE MEMES (3-5 dias)
──────────────────────────────────────────
1. Criar Components/MemeDetector.py
2. Detectar mudanças nos cantos da tela
3. Integrar com pipeline (paralelo ao Whisper)
4. Salvar eventos em meme_events.json
5. Usar no movimento de câmera

RESULTADO ESPERADO: Câmera foca memes automaticamente

🟢 FASE 3: SISTEMA DE PERFIL (5-7 dias)
──────────────────────────────────────────
1. Criar Components/ProfileManager.py
2. Estrutura de dados do perfil lives_do_11closed
3. Integrar review_shorts.py no pipeline
4. Sistema de aprendizado por feedback
5. Ajustar seleção baseado em histórico

RESULTADO ESPERADO: Cada live, seleção 20% melhor

🔵 FASE 4: LEGENDAS AVANÇADAS (2-3 dias)
──────────────────────────────────────────
1. OCR em memes (pytesseract)
2. Legendas de memes (posição/estilo especial)
3. Pós-processamento de gírias
4. Emojis baseados em emoção
5. Legendas conscientes de contexto

RESULTADO ESPERADO: Legendas 100% completas

⚪ FASE 5: OTIMIZAÇÕES (opcional)
──────────────────────────────────────────
1. Paralelização (4 clips simultâneos)
2. Cache de transcrições
3. GPU para Whisper
4. UI web para revisão
5. Upload automático pro YouTube

RESULTADO ESPERADO: 4x mais rápido
"""

# =============================================================================
# PARTE 6: ARQUIVOS QUE EXISTEM MAS NÃO SÃO USADOS
# =============================================================================

ARQUIVOS_ORFAOS = """
PASTA /learning:
- Arquivos de um sistema antigo de ML
- NÃO são usados atualmente
- PODEM SER DELETADOS ou mantidos para referência futura

ARQUIVO force_one_short_test.py:
- Script de teste
- Não faz parte do pipeline
- MANTER para debug

ARQUIVO test_*.py:
- Scripts de teste unitário
- MANTER para desenvolvimento

PASTA /models:
- haarcascade_frontalface_default.xml
- Para detecção de rostos
- NÃO É RELEVANTE para suas lives (sem webcam)
- PODE SER REMOVIDO

ARQUIVOS arquivos_nao_codigo.txt, arquivos_suspeitos.txt:
- Temporários da configuração do Git
- PODEM SER DELETADOS
"""

# =============================================================================
# PARTE 7: CÓDIGO EXEMPLO DE INTEGRAÇÃO COMPLETA
# =============================================================================

EXEMPLO_INTEGRACAO = """
# run_pipeline_v2.py - VERSÃO MELHORADA

from Components.MemeDetector import detect_memes_in_video
from Components.ProfileManager import ProfileManager
from Components.Transcription import transcribeAudio, post_process_transcription

def pipeline_melhorado(input_video, profile_name="lives_do_11closed"):
    # 1. ANÁLISE MULTI-MODAL (paralela)
    print("🔍 Analisando vídeo...")
    
    # Transcrição + picos de áudio
    audio_file = extract_audio(input_video)
    transcription, audio_peaks = transcribeAudio(audio_file)
    
    # Detecção de memes (NOVO)
    meme_events = detect_memes_in_video(input_video)
    print(f"   🎭 {len(meme_events)} memes detectados")
    
    # Enriquecer transcrição (NOVO)
    transcription = post_process_transcription(
        transcription, audio_peaks, meme_events
    )
    
    # 2. CARREGAR PERFIL
    profile = ProfileManager.load(profile_name)
    
    # 3. SELEÇÃO INTELIGENTE
    clips = select_clips_with_profile(
        transcription=transcription,
        meme_events=meme_events,
        audio_peaks=audio_peaks,
        profile=profile
    )
    
    print(f"📌 {len(clips)} clips selecionados")
    
    # 4. RENDERIZAÇÃO
    for clip in clips:
        render_clip_with_memes(
            clip=clip,
            meme_events=meme_events,
            profile=profile
        )
    
    # 5. REVISÃO E APRENDIZADO (NOVO)
    if input("Revisar shorts? (s/n): ").lower() == 's':
        approved, rejected = review_shorts_interactive()
        profile.learn_from_feedback(approved, rejected)
        profile.save()
    
    print(f"✅ {len(clips)} shorts prontos!")
"""

# =============================================================================
# FIM DA ANÁLISE
# =============================================================================

print(__doc__)
print("=" * 70)
print("ANÁLISE COMPLETA SALVA")
print("Próximo passo: Criar arquivos individuais comentados")
print("=" * 70)
