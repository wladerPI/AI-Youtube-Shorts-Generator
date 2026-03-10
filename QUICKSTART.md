# ⚡ GUIA RÁPIDO - AI-Youtube-Shorts-Generator V3

## 🚀 INSTALAÇÃO RÁPIDA

### 1. Clonar repositório:
```bash
git clone https://github.com/wladerPI/AI-Youtube-Shorts-Generator.git
cd AI-Youtube-Shorts-Generator
```

### 2. Instalar dependências:
```bash
pip install -r requirements.txt
```

### 3. Configurar API OpenAI:
Criar arquivo `.env`:
```
OPENAI_API_KEY=sua-chave-aqui
```

### 4. Instalar ffmpeg:
- **Windows:** Baixar de https://ffmpeg.org/download.html
- **Linux:** `sudo apt install ffmpeg`
- **macOS:** `brew install ffmpeg`

---

## 🎬 USO BÁSICO

### GERAR SHORTS:

```bash
python run_pipeline.py input/sua_live.mp4 10 --profile lives_do_11closed
```

**Resultado:**
- 10 shorts em `output/shorts_XXXXX/`
- Cada short tem `.mp4`, `.srt` e `.ass`
- Otimizados e prontos para upload

---

## ⚙️ OPÇÕES AVANÇADAS

### Desabilitar recursos específicos:

```bash
# Sem otimização (não remove silêncios, não acelera)
python run_pipeline.py input/live.mp4 10 --profile meu_perfil --no-optimize

# Sem legendas
python run_pipeline.py input/live.mp4 10 --profile meu_perfil --no-subtitles

# Sem movimento de câmera
python run_pipeline.py input/live.mp4 10 --profile meu_perfil --no-movement
```

---

## 📋 REVISAR SHORTS

Após gerar shorts, revise e aprove:

```bash
python review_shorts.py output/shorts_XXXXX/ --profile lives_do_11closed
```

**Comandos na revisão:**
- **S** = Aprovar
- **N** = Rejeitar (escolhe motivo)
- **P** = Pular
- **Q** = Sair (aplica aprendizado automaticamente)

**O sistema aprende automaticamente!** 🧠

---

## 👤 CRIAR NOVO PERFIL

```python
python -c "from Components.ProfileManager import ProfileManagerV3; pm = ProfileManagerV3(); pm.create_profile('meu_perfil')"
```

Configurações padrão:
- Velocidade: 1.25x
- Remove silêncios: Sim
- Legendas: .srt + .ass
- Movimento de câmera: Sim

---

## 📊 VER ESTATÍSTICAS DO PERFIL

```bash
python apply_learning.py lives_do_11closed --show-stats
```

Mostra:
- Taxa de aprovação
- Motivos de rejeição
- Histórico de ajustes
- Threshold atual

---

## 🎯 WORKFLOW COMPLETO

```bash
# 1. Gerar shorts
python run_pipeline.py input/live.mp4 10 --profile lives_do_11closed

# 2. Revisar (sistema aprende sozinho!)
python review_shorts.py output/shorts_XXXXX/ --profile lives_do_11closed

# 3. Ver estatísticas
python apply_learning.py lives_do_11closed --show-stats

# 4. Upload dos aprovados!
```

---

## ⚡ RECURSOS V3

### ✨ Otimização de Vídeo:
- Remove silêncios > 1 segundo
- Acelera 1.25x (configurável)
- Normaliza áudio

### ✨ Legendas Profissionais:
- PT-BR nativo
- Word-level timing perfeito
- Múltiplos estilos (.srt + .ass)
- CapCut-ready

### ✨ Movimento de Câmera:
- Detecta memes por texto
- Move para esquerda/direita
- Retorna ao centro
- SEM GPU (viável em CPU!)

### ✨ Aprendizado Automático:
- Aprende com cada revisão
- Ajusta thresholds automaticamente
- Melhora com o tempo

---

## 🆘 PROBLEMAS COMUNS

### Erro: "OPENAI_API_KEY not found"
```bash
# Verificar .env
type .env

# Recriar se necessário
echo OPENAI_API_KEY=sua-chave > .env
```

### Erro: "ffmpeg not found"
```bash
# Verificar instalação
ffmpeg -version

# Adicionar ao PATH se necessário
```

### Shorts sem áudio:
- ✅ **RESOLVIDO** no V3!
- VerticalCropper agora usa ffmpeg para adicionar áudio

---

## 📚 MAIS INFORMAÇÕES

- **Instalação completa:** `INSTALLATION.md`
- **Documentação detalhada:** `USAGE.md`
- **Histórico de versões:** `CHANGELOG.md`
- **Guia completo V3:** `GUIA_COMPLETO_V2.md`

---

## 💡 DICAS PRO

1. **Teste primeiro com vídeo curto** (5-10 min)
2. **Revise TODOS os shorts** (sistema aprende!)
3. **Veja estatísticas regularmente**
4. **Ajuste keywords no perfil** se necessário

---

**BOM TRABALHO! 🎬🔥**
