# 🚀 GUIA DE INTEGRAÇÃO - SISTEMA HÍBRIDO (Áudio + Visual)

## 📋 **RESUMO DA SOLUÇÃO FINAL**

### **Sistema Híbrido = 80% Áudio + 20% Visual**

```
┌─────────────────────────────────────────────────────────────┐
│              DETECÇÃO DE MOMENTOS ENGRAÇADOS                │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        │                                       │
  ┌─────▼──────┐                      ┌────────▼────────┐
  │  ÁUDIO 80% │                      │  VISUAL 20%     │
  │            │                      │                 │
  │ [RISO]     │                      │ Mudanças nos    │
  │ Transcrição│                      │ cantos          │
  │ GPT + Memes│                      │ Screenshots     │
  └─────┬──────┘                      └────────┬────────┘
        │                                      │
        └───────────────────┬──────────────────┘
                            ↓
                ┌───────────────────────┐
                │  60-100 CLIPS TOTAIS  │
                └───────────────────────┘
                            ↓
                ┌───────────────────────┐
                │  VOCÊ REVISA          │
                │  (review_shorts.py)   │
                └───────────────────────┘
                            ↓
                ┌───────────────────────┐
                │  ProfileManager       │
                │  aprende preferências │
                └───────────────────────┘
                            ↓
                ┌───────────────────────┐
                │  40-60 SHORTS FINAIS  │
                └───────────────────────┘
```

---

## ✅ **ARQUIVOS JÁ PRONTOS**

### **Componentes Principais:**
1. ✅ `Components/LanguageTasks.py` - Personalizado com 50+ memes
2. ✅ `Components/MemeDetector.py` - V3 Final (visual sem OCR)
3. ✅ `Components/ProfileManager.py` - Sistema de aprendizado
4. ✅ `Render/CameraControllerV2.py` - Movimento inteligente

### **Componentes Existentes (funcionam):**
5. ✅ `Components/Transcription.py` - Whisper + [RISO]
6. ✅ `Components/SubtitleGenerator.py` - Legendas PT-BR
7. ✅ `run_pipeline.py` - Pipeline principal

---

## 🔧 **INTEGRAÇÃO PASSO A PASSO**

### **PASSO 1: Atualizar run_pipeline.py**

Adicionar detecção de memes **em paralelo** com transcrição:

```python
# run_pipeline.py (linha ~80, após extract_audio)

print("🎤 Transcrevendo áudio...")
transcriptions = transcribeAudio(audio_file)

# NOVO: Detectar memes visuais EM PARALELO
print("🎭 Detectando memes visuais...")
from Components.MemeDetector import detect_memes_in_video
meme_events = detect_memes_in_video(
    video_path=input_video,
    session_id=session,
    sample_interval=3.0  # 1 frame a cada 3s
)
print(f"   ✅ {len(meme_events)} eventos visuais detectados")
```

---

### **PASSO 2: Passar meme_events para seleção**

```python
# run_pipeline.py (linha ~120, ao chamar select_segments)

segments = select_segments_with_llm(
    transcriptions=transcriptions,
    max_segments=max_shorts,
    min_duration=45,
    max_duration=180,
    meme_events=meme_events  # NOVO parâmetro
)
```

---

### **PASSO 3: Atualizar SegmentSelectorLLM.py**

```python
# Components/SegmentSelectorLLM.py

def select_segments_with_llm(
    transcriptions,
    max_segments=25,
    min_duration=30,
    max_duration=180,
    prefer_llm=True,
    video_duration_min=240,
    meme_events=None  # NOVO
):
    # ... código existente ...
    
    highlights = GetHighlights(transcript_text, video_duration_min)
    
    # NOVO: Adicionar eventos visuais aos highlights
    if meme_events:
        for meme in meme_events:
            # Criar clip ao redor do meme visual
            highlights.append({
                "start": max(0, meme['timestamp'] - 30),
                "end": meme['timestamp'] + 30,
                "reason": f"meme visual em {meme['position']}",
                "score": 1.2,  # Score um pouco maior
                "meme_screenshot": meme['screenshot_corner']
            })
    
    # ... resto do código ...
```

---

### **PASSO 4: Integrar ProfileManager**

```python
# run_pipeline.py (no início, após imports)

from Components.ProfileManager import load_profile

# Carregar perfil
profile = load_profile("lives_do_11closed")
profile.start_new_live()

# Obter preferências
prefs = profile.get_selection_preferences()
print(f"📊 Perfil carregado: {prefs['approval_rate']*100:.1f}% aprovação")
```

---

### **PASSO 5: Passar meme_events para CameraController**

```python
# Render/VerticalCropper.py (modificar função existente)

def render_vertical_video(
    video_in,
    video_out,
    meme_events=None,  # NOVO
    session_id=None
):
    # ... código existente ...
    
    # NOVO: Usar CameraControllerV2 se tiver memes
    if meme_events:
        from Render.CameraControllerV2 import CameraControllerV2
        
        controller = CameraControllerV2(
            video_width=video.width,
            video_height=video.height,
            output_width=1080,
            output_height=1920,
            meme_events=meme_events,
            fps=video.fps
        )
        
        # Para cada frame, usar posição da câmera
        for frame_num in range(total_frames):
            time = frame_num / fps
            camera_x, state = controller.get_camera_position(time)
            crop_box = controller.calculate_crop_box(camera_x, frame.height)
            # ... aplicar crop ...
```

---

### **PASSO 6: Sistema de Revisão (Opcional mas Recomendado)**

Após gerar os shorts, permitir revisão:

```python
# run_pipeline.py (no final, após gerar todos shorts)

# Perguntar se quer revisar
resposta = input("\n📝 Revisar shorts gerados? (s/n): ")
if resposta.lower() == 's':
    from review_shorts import review_shorts_interactive
    
    approved, rejected = review_shorts_interactive(session)
    
    # Aprender com feedback
    for short in approved:
        profile.learn_from_review(short, approved=True)
    for short in rejected:
        profile.learn_from_review(short, approved=False)
    
    profile.save()
    profile.generate_insights_report()
```

---

## 📊 **FLUXO COMPLETO INTEGRADO**

```python
# PSEUDOCÓDIGO DO PIPELINE FINAL

# 1. ANÁLISE MULTI-MODAL
audio_file = extract_audio(input_video)
transcriptions = transcribeAudio(audio_file)  # Com [RISO]
meme_events = detect_memes_in_video(input_video, session)

# 2. CARREGAR PERFIL
profile = load_profile("lives_do_11closed")
profile.start_new_live()
prefs = profile.get_selection_preferences()

# 3. SELEÇÃO INTELIGENTE
highlights_audio = GetHighlights(transcriptions)  # 60 clips
highlights_visual = [meme para clip em meme_events]  # 40 clips
all_highlights = highlights_audio + highlights_visual  # 100 clips

# Filtrar e ordenar por score
all_highlights = sorted(all_highlights, key=lambda x: x['score'], reverse=True)
top_clips = all_highlights[:max_shorts]  # Top 50

# 4. RENDERIZAÇÃO
for clip in top_clips:
    render_clip_with_memes(
        clip=clip,
        meme_events=meme_events,
        profile=profile
    )

# 5. REVISÃO E APRENDIZADO
approved, rejected = review_shorts_interactive()
for short in approved:
    profile.learn_from_review(short, approved=True)

profile.save()
profile.generate_insights_report()
```

---

## 🎯 **RESULTADO ESPERADO**

### **Live de 5 horas:**
- 🎤 Áudio detecta: **60 momentos** ([RISO] + frases)
- 🎭 Visual detecta: **40 momentos** (mudanças grandes)
- 📊 Total: **100 clips** gerados

### **Após revisão:**
- ✅ Você aprova: **60 shorts**
- ❌ Você rejeita: **40 shorts**
- 💾 Sistema aprende: Próxima live → **70 aprovados** (melhora contínua)

### **Qualidade:**
- 🎥 Câmera foca em memes (quando detectados)
- 📝 Legendas completas em PT-BR
- ⏱️ Durações corretas (45-180s)
- 🎯 Clips com contexto completo

---

## ⚙️ **AJUSTES FINOS**

### **Se detectar MUITOS memes visuais:**
```python
# MemeDetector.py linha 120
change_threshold=0.80  # Aumentar de 0.70
sample_interval=5.0    # Aumentar de 3.0
```

### **Se detectar POUCOS:**
```python
change_threshold=0.60  # Diminuir
sample_interval=2.0    # Diminuir
```

### **Se filtros matarem clips:**
```python
# run_pipeline.py linhas 113-120
# Comentar essas linhas:
# segments = _deduplicate_segments(segments, min_gap=60)
# segments = filter_by_time_distance(segments, min_distance=60)
```

---

## 🚀 **ORDEM DE IMPLEMENTAÇÃO**

### **Semana 1: Básico funcionando**
1. ✅ Substituir LanguageTasks.py (personalizado)
2. ✅ Substituir MemeDetector.py (V3)
3. ✅ Testar separadamente

### **Semana 2: Integração**
4. ✅ Integrar MemeDetector no run_pipeline.py
5. ✅ Passar meme_events para CameraController
6. ✅ Testar pipeline completo

### **Semana 3: Aprendizado**
7. ✅ Integrar ProfileManager
8. ✅ Integrar review_shorts.py
9. ✅ Rodar primeira live completa

### **Semana 4: Refinamento**
10. ✅ Ajustar parâmetros baseado nos resultados
11. ✅ Adicionar mais memes na biblioteca
12. ✅ Gerar relatório de insights

---

## 📋 **CHECKLIST DE INTEGRAÇÃO**

- [ ] LanguageTasks.py substituído e testado
- [ ] MemeDetector.py V3 substituído e testado
- [ ] ProfileManager.py adicionado
- [ ] CameraControllerV2.py adicionado
- [ ] run_pipeline.py modificado (adicionar meme detection)
- [ ] SegmentSelectorLLM.py modificado (aceitar meme_events)
- [ ] VerticalCropper.py modificado (usar CameraControllerV2)
- [ ] review_shorts.py integrado
- [ ] Teste com live curta (30min)
- [ ] Teste com live completa (5h)
- [ ] Primeira revisão e ajustes
- [ ] Sistema de aprendizado funcionando
- [ ] Documentação atualizada no GitHub

---

## 💡 **DICAS IMPORTANTES**

1. **Comece pequeno:** Teste com live de 30min primeiro
2. **Revise sempre:** Sistema melhora 20-30% a cada live
3. **Screenshots:** Sempre revise os memes visuais detectados
4. **Perfil:** Gere relatório após cada live
5. **Backup:** Mantenha perfil salvo (profiles/lives_do_11closed/)

---

## 🆘 **TROUBLESHOOTING**

### **Problema: Poucos clips gerados**
- Diminuir change_threshold no MemeDetector
- Comentar filtros no run_pipeline.py
- Verificar se [RISO] está sendo detectado

### **Problema: Muitos clips ruins**
- Aumentar change_threshold
- Revisar e rejeitar → sistema aprende

### **Problema: Câmera não foca memes**
- Verificar se meme_events está sendo passado
- Testar CameraControllerV2 standalone
- Ajustar corner_margin

---

**Boa sorte com a integração! 🚀**
