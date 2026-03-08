# 🎬 AI-Youtube-Shorts-Generator

> **Sistema profissional de IA para geração automática de shorts de alta qualidade a partir de lives de gameplay**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)](https://openai.com/)

---

## 🌟 **Destaques**

- 🎭 **Detecção inteligente de memes** - Reconhece automaticamente seus 79 memes personalizados
- 😂 **Análise de risadas** - Identifica concentrações de risadas e momentos engraçados
- 🧠 **Aprendizado de máquina** - Sistema aprende suas preferências e melhora a cada live
- 🎯 **Multi-perfil** - Suporte para múltiplos criadores com preferências individuais
- 🔊 **Áudio perfeito** - Todos os shorts gerados com áudio sincronizado
- 📊 **Taxa de aprovação 70%+** - Depois de 3 lives revisadas

---

## 📋 **Índice**

- [Funcionalidades](#-funcionalidades)
- [Demo](#-demo)
- [Instalação](#-instalação-rápida)
- [Uso Rápido](#-uso-rápido)
- [Documentação Completa](#-documentação)
- [Como Funciona](#-como-funciona)
- [Requisitos](#-requisitos)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## ✨ **Funcionalidades**

### **Sistema de Pontuação Profissional**
- ✅ **Análise de Áudio** - Detecta energia de voz, intensidade e momentos impactantes
- ✅ **Análise de Contexto (GPT-4)** - Identifica narrativas, frases marcantes e contexto
- ✅ **Detecção de Memes** - Reconhece palavras e frases dos seus memes configurados
- ✅ **Concentração de Risadas** - Prioriza momentos com múltiplas risadas
- ✅ **Score Combinado** - Pontuação final considera todos os fatores (até 30+ pontos!)

### **Sistema de Aprendizado**
- 🧠 **Revisão Interativa** - Interface simples S/N para aprovar/rejeitar shorts
- 🧠 **Ajuste Automático** - Thresholds se adaptam baseado nas suas avaliações
- 🧠 **Multi-perfil** - Cada criador tem suas próprias preferências
- 🧠 **Melhoria Contínua** - Cada live gera shorts melhores que a anterior

### **Qualidade Profissional**
- 🎥 **Formato Vertical** - 1080x1920 pronto para YouTube Shorts/TikTok/Reels
- 🔊 **Áudio Sincronizado** - Extração e renderização com áudio perfeito
- ⚡ **Otimizado para CPU** - Funciona sem GPU (transcrição em chunks)
- 📊 **Validação de Qualidade** - Verifica qualidade da transcrição automaticamente

---

## 🎥 **Demo**

### **Entrada: Live de 4 horas**
```
input/live_cortado.mp4
├─ Duração: 4h 11min
├─ Resolução: 1280x720
└─ Áudio: AAC 127kbps
```

### **Saída: 10 shorts de alta qualidade**
```
output/shorts_XXXXXX/
├─ short_001.mp4 (60s) - Score: 18.2 🎭🎭😂
├─ short_002.mp4 (75s) - Score: 15.8 🎭😂
├─ short_003.mp4 (60s) - Score: 14.3 😂😂
└─ ... (10 shorts totais)

Taxa de aprovação: 70%+
Tempo de processamento: ~45 minutos
```

---

## 🚀 **Instalação Rápida**

### **Pré-requisitos**
- Python 3.11+
- FFmpeg
- OpenAI API Key
- 8GB+ RAM

### **Instalação em 3 passos:**

```bash
# 1. Clonar repositório
git clone https://github.com/seu-usuario/AI-Youtube-Shorts-Generator.git
cd AI-Youtube-Shorts-Generator

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar API
cp .env.example .env
# Editar .env e adicionar sua OPENAI_API_KEY
```

📚 **[Guia de Instalação Completo →](INSTALLATION.md)**

---

## ⚡ **Uso Rápido**

### **Gerar shorts de uma live:**

```bash
# 1. Processar live (gera 10 shorts)
python run_pipeline_PROFESSIONAL_V2.py input/minha_live.mp4 10 --profile meu_canal

# 2. Revisar shorts (S = aprova, N = rejeita)
python review_shorts.py output/shorts_XXXXXX/ --profile meu_canal

# 3. Pronto! Sistema aprendeu automaticamente
# Próxima live terá shorts ainda melhores!
```

📚 **[Guia de Uso Completo →](USAGE.md)**

---

## 📚 **Documentação**

| Documento | Descrição |
|-----------|-----------|
| **[INSTALLATION.md](INSTALLATION.md)** | Instalação passo a passo detalhada |
| **[USAGE.md](USAGE.md)** | Como usar todas as funcionalidades |
| **[CONFIGURATION.md](CONFIGURATION.md)** | Configuração e personalização |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Como o sistema funciona internamente |
| **[CHANGELOG.md](CHANGELOG.md)** | Histórico de versões e atualizações |

---

## 🔧 **Como Funciona**

### **Pipeline de Processamento (7 passos):**

```
1️⃣ EXTRAÇÃO DE ÁUDIO
   ↓ FFmpeg extrai áudio em 16kHz mono
   
2️⃣ TRANSCRIÇÃO (Whisper)
   ↓ Transcreve em PT-BR com timestamps
   ↓ Detecta [RISO] e risadas
   
3️⃣ VALIDAÇÃO
   ↓ Verifica qualidade da transcrição
   
4️⃣ ANÁLISE DE ÁUDIO
   ↓ Energia de voz, intensidade, risadas
   
5️⃣ ANÁLISE DE CONTEXTO (GPT-4)
   ↓ Identifica narrativas, frases, contexto
   
6️⃣ PONTUAÇÃO DE MEMES
   ↓ Detecta palavras dos seus 79 memes
   ↓ Calcula concentração de risadas
   
7️⃣ SELEÇÃO E RENDERIZAÇÃO
   ↓ Seleciona TOP 10 por score
   ↓ Renderiza 1080x1920 com áudio
```

### **Sistema de Pontuação:**

```python
Score Final = (Áudio + Contexto + Memes + Risadas) × Bônus

EXEMPLO:
├─ 2 risadas: +3.0
├─ Energia alta: +1.0
├─ GPT detectou frase marcante: ×1.3
├─ 2 memes detectados: +4.0, ×1.5
├─ COMBO (áudio + contexto + memes): ×1.5
└─ Score Final: 18.2 pontos! ⭐⭐⭐
```

📚 **[Arquitetura Completa →](ARCHITECTURE.md)**

---

## 💻 **Requisitos**

### **Hardware Recomendado:**
- **CPU:** 4+ cores
- **RAM:** 8GB+ (16GB recomendado)
- **Disco:** 20GB+ espaço livre
- **GPU:** Opcional (acelera transcrição)

### **Software:**
- **Python:** 3.11 ou superior
- **FFmpeg:** Última versão
- **Sistema:** Windows 10/11, Linux, macOS

### **APIs:**
- **OpenAI API:** GPT-4 (para análise de contexto)

---

## 🎯 **Roadmap**

- [x] Sistema básico de geração de shorts
- [x] Detecção de memes personalizada
- [x] Sistema de aprendizado multi-perfil
- [x] Validação de transcrição
- [x] Áudio sincronizado
- [ ] Detecção visual de memes (template matching)
- [ ] Suporte para múltiplos idiomas
- [ ] Interface web (dashboard)
- [ ] Análise de sentimentos
- [ ] Detecção automática de thumbnails

---

## 🤝 **Contribuindo**

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📝 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 **Autor**

Desenvolvido com ❤️ para criadores de conteúdo de gameplay

---

## 🙏 **Agradecimentos**

- **OpenAI** - GPT-4 e Whisper
- **FFmpeg** - Processamento de vídeo
- **Comunidade Python** - Bibliotecas incríveis

---

## 📧 **Suporte**

Encontrou um bug? Tem uma sugestão?

- 🐛 [Reportar Bug](https://github.com/seu-usuario/AI-Youtube-Shorts-Generator/issues)
- 💡 [Sugerir Feature](https://github.com/seu-usuario/AI-Youtube-Shorts-Generator/issues)
- 📧 Email: seu-email@exemplo.com

---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela! ⭐**

[![GitHub stars](https://img.shields.io/github/stars/seu-usuario/AI-Youtube-Shorts-Generator.svg?style=social&label=Star)](https://github.com/seu-usuario/AI-Youtube-Shorts-Generator)

</div>
