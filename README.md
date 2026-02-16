# 🎬 AI Youtube Shorts Generator

## ⚠️ **STATUS: EM DESENVOLVIMENTO - PROBLEMAS CRÍTICOS CONHECIDOS**

Sistema para gerar Shorts virais de lives de 5+ horas. **Atualmente com problemas que impedem uso efetivo.**

---

## 🚨 **PROBLEMAS CRÍTICOS**

### **1. FILTROS MUITO AGRESSIVOS (99% de rejeição)**
- **Sintoma:** 500 clips → 4 shorts finais
- **Causa:** `min_gap=60s` em `run_pipeline.py` linhas 113-120
- **Solução:** Reduzir para 20s ou comentar filtros

### **2. GPT INCONSISTENTE**
- **Sintoma:** Às vezes retorna clips de 2s, às vezes 60s
- **Causa:** Prompt genérico em `LanguageTasks.py`
- **Solução:** Few-shot learning ou análise de áudio direto

### **3. QUALIDADE BAIXA**
- **Sintoma:** Shorts sem contexto, cortam frases
- **Causa:** GPT não vê vídeo, só transcrição
- **Solução:** Análise visual + áudio combinados

---

## 📊 **FLUXO ATUAL**

```
live.mp4 → Whisper → GPT → Filtros → 2-4 shorts
         (10min)   (30s)   (MATA   (ruins)
                            TUDO)
```

---

## 🔧 **ARQUIVOS COMENTADOS**

Todos os arquivos `.py` têm comentários explicando:
- ⚠️ Problemas conhecidos
- 🔧 Onde corrigir
- ✅ O que funciona
- 🎯 Próximos passos

**Leia os comentários em:**
1. `Components/LanguageTasks.py`
2. `Components/SegmentSelectorLLM.py`
3. `run_pipeline.py`

---

## 🎯 **ROADMAP**

### 🔴 URGENTE:
1. Resolver filtros (`run_pipeline.py`)
2. Melhorar GPT (`LanguageTasks.py`)
3. Adicionar logs

### 🟡 IMPORTANTE:
1. Cache de transcrições
2. Paralelização
3. Modo preview

### 🟢 FUTURO:
1. UI Web
2. Análise sem GPT
3. Upload automático

---

## 💻 **INSTALAÇÃO**

```bash
pip install openai-whisper librosa
```

Configurar `.env`:
```
OPENAI_API_KEY=sk-proj-...
```

---

## 🚀 **USO**

```bash
python run_pipeline.py input/video.mp4
```

**Resultado esperado:** 2-4 shorts (deveria ser 30-50)

---

## 📞 **CONTINUIDADE**

Projeto pausado. Para retomar:
1. Ler este README
2. Ver comentários nos arquivos
3. Corrigir seção 🔴 URGENTE
4. Testar com vídeo curto (30min)

**Contato:** wlader.pi@gmail.com

---

**Versão:** 0.2.0-alpha  
**Status:** ⚠️ Não estável  
**Licença:** MIT
