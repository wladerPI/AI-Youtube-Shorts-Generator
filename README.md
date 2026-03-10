# 🎬 AI-Youtube-Shorts-Generator V3

> **O melhor gerador de shorts automático do mundo** 🏆

Sistema profissional para transformar lives/vídeos longos em shorts virais usando IA.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Produção-success.svg)]()

---

## ✨ FEATURES V3.0

### 🎯 **Seleção Inteligente**
- ✅ Detecta **79 memes personalizados** do streamer
- ✅ Análise de áudio (risadas, energia, intensidade)
- ✅ Análise de contexto com GPT-4
- ✅ Sistema de pontuação híbrido (10+ fatores)
- ✅ Aprendizado automático por perfil

### ⚡ **Otimização de Vídeo** (NOVO V3!)
- ✅ Remove silêncios automático (>1s)
- ✅ Acelera vídeo 1.25x (configurável 1.0x-1.3x)
- ✅ Normalização de áudio profissional
- ✅ Mantém sincronia perfeita

### 📝 **Legendas Profissionais** (NOVO V3!)
- ✅ Word-level timing (milissegundos)
- ✅ PT-BR nativo
- ✅ Exporta .SRT + .ASS
- ✅ Múltiplos estilos (Hormozi, MrBeast, Gaming)
- ✅ CapCut-ready

### 🎥 **Movimento de Câmera** (NOVO V3!)
- ✅ Detecta memes por TEXTO (sem GPU!)
- ✅ Move câmera para esquerda/direita
- ✅ Retorna ao centro automaticamente
- ✅ Processamento viável em CPU

### 🧠 **Aprendizado Contínuo**
- ✅ Sistema de revisão interativo
- ✅ Aprende automaticamente após cada sessão
- ✅ Ajusta thresholds baseado em taxa de aprovação
- ✅ Multi-perfil com configurações independentes

---

## 🚀 INSTALAÇÃO RÁPIDA

```bash
# 1. Clonar
git clone https://github.com/wladerPI/AI-Youtube-Shorts-Generator.git
cd AI-Youtube-Shorts-Generator

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar API
echo OPENAI_API_KEY=sua-chave-aqui > .env

# 4. Instalar ffmpeg
# Windows: https://ffmpeg.org/download.html
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

📚 **[Guia completo de instalação →](INSTALLATION.md)**

---

## 💻 USO

### **Gerar Shorts:**

```bash
python run_pipeline.py input/live.mp4 10 --profile lives_do_11closed
```

**Resultado:**
```
output/shorts_20260310_163045/
├── short_001.mp4  ✅ Otimizado + Legendas
├── short_001.srt  ✅ Legendas PT-BR
├── short_001.ass  ✅ Legendas estilizadas
├── short_002.mp4
├── ...
└── short_010.mp4
```

### **Revisar e Aprender:**

```bash
python review_shorts.py output/shorts_XXXXX/ --profile lives_do_11closed
```

Sistema aprende automaticamente! 🧠

📚 **[Documentação completa →](USAGE.md)**

---

## 🎯 DIFERENCIAIS

### **O QUE OUTROS NÃO TÊM:**

✅ **79 memes personalizados detectados**
- Análise textual de frases marcantes do streamer
- Detecção por palavras-chave configuráveis

✅ **Aprendizado contínuo por perfil**
- Sistema aprende suas preferências
- Ajusta automaticamente baseado em aprovações

✅ **Otimização profissional**
- Remove pausas chatas
- Acelera para manter ritmo
- Áudio normalizado

✅ **Legendas prontas para CapCut**
- Timing perfeito
- Múltiplos estilos
- Exportação .srt/.ass

✅ **100% Open Source e Customizável**
- Código limpo e documentado
- Fácil adicionar novos memes
- Configurável por perfil

---

## 📦 COMPONENTES V3

### **Core:**
- `run_pipeline.py` - Pipeline completo 7 passos
- `review_shorts.py` - Sistema de revisão interativo
- `apply_learning.py` - Aplicar aprendizado manual

### **Components:**
- `AudioAnalyzer` - Análise de áudio (risadas, energia)
- `ContextAnalyzer` - Análise GPT-4 de contexto
- `MemeScorer` - Detecção de 79 memes
- `ClipSelector` - Seleção inteligente
- `ProfileManager` - Gestão de perfis com aprendizado
- `SubtitleGenerator` - Legendas profissionais ⭐ NOVO
- `VideoOptimizer` - Otimização de vídeo ⭐ NOVO
- `TranscriptionValidator` - Validação de qualidade

### **Render:**
- `VerticalCropper` - Crop vertical 9:16
- `SmartCropper` - Movimento de câmera ⭐ NOVO
- `CameraController` - Controle de câmera

---

## 🎮 EXEMPLO: CANAL "11closed"

**Live de Dreadway (4h):**
- 📊 Input: 1 live completa
- ⚡ Processamento: ~80 minutos
- 🎬 Output: 10 shorts otimizados
- 📝 Legendas: PT-BR automáticas
- ✅ Taxa de aprovação: 70%+

**Memes detectados:**
- "Puta que pariu!" (21x)
- "Chama a polícia!" (8x)
- "Já acabou Jessica" (5x)
- ... (79 memes configurados)

---

## ⚙️ REQUISITOS

### **Sistema:**
- Python 3.8+
- 16GB RAM (recomendado)
- CPU multi-core (GPU opcional)

### **Dependências principais:**
- OpenAI API (GPT-4)
- Whisper (transcrição)
- opencv-python (vídeo)
- librosa (áudio)
- ffmpeg (processamento)

---

## 📚 DOCUMENTAÇÃO

- 📖 [Guia Rápido](QUICKSTART.md)
- 📖 [Instalação Completa](INSTALLATION.md)
- 📖 [Documentação de Uso](USAGE.md)
- 📖 [Changelog](CHANGELOG.md)
- 📖 [Guia Completo V3](GUIA_COMPLETO_V2.md)

---

## 🤝 CONTRIBUIR

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 LICENÇA

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 CRÉDITOS

Desenvolvido por **[@wladerPI](https://github.com/wladerPI)**

Criado especialmente para o canal **11closed** (lives de Dreadway)

---

<div align="center">

**🎬 Feito com ❤️ para criadores de conteúdo 🎬**

⭐ **Se gostou, deixe uma estrela!** ⭐

</div>
