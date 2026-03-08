# 📦 Guia de Instalação Completo

Este guia detalha todos os passos necessários para instalar e configurar o AI-Youtube-Shorts-Generator do zero.

---

## 📋 **Índice**

- [Pré-requisitos](#pré-requisitos)
- [Instalação do Python](#1-instalação-do-python)
- [Instalação do FFmpeg](#2-instalação-do-ffmpeg)
- [Clonar o Repositório](#3-clonar-o-repositório)
- [Configurar Ambiente Virtual](#4-configurar-ambiente-virtual)
- [Instalar Dependências](#5-instalar-dependências)
- [Configurar API do OpenAI](#6-configurar-api-do-openai)
- [Configurar Memes](#7-configurar-seus-memes)
- [Verificar Instalação](#8-verificar-instalação)
- [Troubleshooting](#troubleshooting)

---

## ✅ **Pré-requisitos**

### **Hardware Mínimo:**
- **CPU:** Intel i5 / AMD Ryzen 5 (4+ cores)
- **RAM:** 8GB (16GB recomendado)
- **Disco:** 20GB espaço livre
- **GPU:** Opcional (acelera transcrição)

### **Software:**
- **Sistema Operacional:** Windows 10/11, Linux, ou macOS
- **Conexão:** Internet para download e uso da API
- **Permissões:** Administrador (para instalar dependências)

---

## 1️⃣ **Instalação do Python**

### **Windows:**

1. **Baixar Python 3.11+:**
   - Acesse: https://www.python.org/downloads/
   - Baixe Python 3.11 ou superior

2. **Instalar:**
   - Execute o instalador
   - ✅ **IMPORTANTE:** Marque "Add Python to PATH"
   - Clique em "Install Now"

3. **Verificar:**
   ```bash
   python --version
   # Deve mostrar: Python 3.11.x ou superior
   ```

### **Linux:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Verificar
python3 --version
```

### **macOS:**

```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python
brew install python@3.11

# Verificar
python3 --version
```

---

## 2️⃣ **Instalação do FFmpeg**

FFmpeg é necessário para processar vídeos e áudio.

### **Windows:**

**Opção 1: Download direto (Recomendado)**

1. Acesse: https://www.gyan.dev/ffmpeg/builds/
2. Baixe: `ffmpeg-release-full.7z`
3. Extrair para: `C:\ffmpeg`
4. Adicionar ao PATH:
   - Win + R → `sysdm.cpl` → Enter
   - Aba "Avançado" → "Variáveis de Ambiente"
   - Em "Path" → Editar → Novo
   - Adicionar: `C:\ffmpeg\bin`
   - OK, OK, OK

**Opção 2: Chocolatey**

```bash
choco install ffmpeg
```

**Verificar:**
```bash
ffmpeg -version
# Deve mostrar informações do FFmpeg
```

### **Linux:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Verificar
ffmpeg -version
```

### **macOS:**

```bash
brew install ffmpeg

# Verificar
ffmpeg -version
```

---

## 3️⃣ **Clonar o Repositório**

```bash
# Escolher uma pasta (ex: F:\AI-Shorts)
# cd /d F:\AI-Shorts

# Clonar o projeto
git clone https://github.com/seu-usuario/AI-Youtube-Shorts-Generator.git

# Entrar na pasta
cd AI-Youtube-Shorts-Generator
```

**Estrutura esperada:**
```
AI-Youtube-Shorts-Generator/
├── Components/
├── Render/
├── meme_templates/
├── input/
├── output/
├── run_pipeline_PROFESSIONAL_V2.py
├── review_shorts.py
├── requirements.txt
└── README.md
```

---

## 4️⃣ **Configurar Ambiente Virtual**

Ambiente virtual isola as dependências do projeto.

### **Windows:**

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar
.venv\Scripts\activate

# Deve aparecer: (.venv) antes do prompt
```

### **Linux/macOS:**

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar
source .venv/bin/activate

# Deve aparecer: (.venv) antes do prompt
```

**Para desativar (quando terminar):**
```bash
deactivate
```

---

## 5️⃣ **Instalar Dependências**

Com o ambiente virtual ativado:

```bash
# Instalar todas as dependências
pip install -r requirements.txt
```

**Dependências principais:**
- `openai` - API do OpenAI (GPT-4, Whisper)
- `whisper` - Transcrição de áudio
- `opencv-python` - Processamento de vídeo
- `librosa` - Análise de áudio
- `pydub` - Manipulação de áudio
- `numpy` - Computação numérica
- `langchain` - Framework para LLMs
- `python-dotenv` - Carregar variáveis de ambiente

**Tempo estimado:** 5-10 minutos

---

## 6️⃣ **Configurar API do OpenAI**

### **1. Obter API Key:**

1. Acesse: https://platform.openai.com/
2. Faça login ou crie uma conta
3. Vá em: API Keys
4. Clique em: "Create new secret key"
5. Copie a chave (começa com `sk-proj-...`)
6. **GUARDE EM LOCAL SEGURO!**

### **2. Configurar no projeto:**

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# OU no Windows:
copy .env.example .env
```

### **3. Editar .env:**

Abrir `.env` com editor de texto e substituir:

```env
OPENAI_API_KEY=SUA-API-DO-OPENAI
```

Por:

```env
OPENAI_API_KEY=sk-proj-j5HRP6Ubq5iqjn2YsI...
```

**⚠️ IMPORTANTE:**
- Nunca compartilhe sua API key
- Não faça commit do arquivo `.env`
- O `.gitignore` já está configurado para ignorá-lo

### **4. Verificar créditos:**

- Acesse: https://platform.openai.com/usage
- Certifique-se de ter créditos suficientes
- ~$0.50-$2.00 por live processada

---

## 7️⃣ **Configurar Seus Memes**

O sistema detecta seus memes personalizados!

### **1. Preparar imagens dos memes:**

```
meme_templates/
├── A - Abelha.png
├── A - Amongus.png
├── B - Batata.png
└── ... (seus 79 memes)
```

**Regras para nomes:**
- ✅ Sem acentos: `Dancando.png` (não `Dançando.png`)
- ✅ Sem espaços problemáticos
- ✅ Formato PNG ou JPG

### **2. Configurar meme_config.json:**

```json
{
  "A - Abelha": {
    "description": "abelha zumbindo bzz bzz",
    "category": "animais",
    "keywords": ["abelha", "bzz", "zumbindo"]
  },
  "B - Batata": {
    "description": "batata assando forno quente",
    "category": "comida",
    "keywords": ["batata", "assar", "forno"]
  }
}
```

**⚠️ IMPORTANTE:**
- `description`: Frases que aparecem quando o meme é usado
- Sistema detecta essas palavras na transcrição
- Quanto mais específico, melhor a detecção

### **3. Exemplo completo:**

Se você fala "olha a abelha zumbindo bzz bzz" na live:
- Sistema detecta palavras em `description`
- Identifica o meme "A - Abelha"
- Aumenta score desse momento!

---

## 8️⃣ **Verificar Instalação**

### **Script de verificação:**

```bash
python verificar_instalacao.py
```

**Saída esperada:**
```
✅ Python 3.11.9
✅ FFmpeg 2025-07-21
✅ Dependências instaladas
✅ OPENAI_API_KEY configurada
✅ Meme templates encontrados: 79
✅ meme_config.json válido

🎉 Instalação completa!
```

### **Teste rápido:**

```bash
# Testar com vídeo curto (1-2 min)
python run_pipeline_PROFESSIONAL_V2.py input/teste.mp4 5 --profile teste

# Deve processar sem erros
```

---

## 🐛 **Troubleshooting**

### **Erro: "Python não é reconhecido"**

**Solução:**
1. Reinstalar Python marcando "Add to PATH"
2. OU adicionar manualmente ao PATH

### **Erro: "FFmpeg não encontrado"**

**Solução Windows:**
```bash
# Verificar se está no PATH
where ffmpeg

# Se não aparecer, adicionar manualmente ao PATH
```

**Solução Linux:**
```bash
which ffmpeg
# Se vazio, instalar: sudo apt install ffmpeg
```

### **Erro: "API key inválida"**

**Solução:**
1. Verificar se copiou a chave completa
2. Verificar se não tem espaços extras
3. Gerar nova chave no OpenAI

### **Erro: "ModuleNotFoundError"**

**Solução:**
```bash
# Verificar se ambiente virtual está ativado
# Deve ter (.venv) no prompt

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### **Erro: "Out of memory"**

**Solução:**
- Usar vídeos menores (< 2 horas)
- Fechar outros programas
- Aumentar memória virtual do Windows

### **Transcrição muito lenta**

**Solução:**
- Normal em CPU (30-60 min para 4h de live)
- Para acelerar: usar GPU (CUDA)
- OU processar lives menores

### **Memes não detectados**

**Solução:**
1. Verificar `meme_config.json`
2. Confirmar que as palavras aparecem na transcrição
3. Testar com frases mais comuns

---

## 🎓 **Próximos Passos**

✅ Instalação completa!

**Agora:**
1. 📚 Ler: [USAGE.md](USAGE.md) - Como usar o sistema
2. ⚙️ Ler: [CONFIGURATION.md](CONFIGURATION.md) - Personalizar configurações
3. 🚀 Processar sua primeira live!

---

## 📞 **Precisa de Ajuda?**

- 🐛 [Reportar problema](https://github.com/seu-usuario/AI-Youtube-Shorts-Generator/issues)
- 💬 Discussões: [GitHub Discussions](https://github.com/seu-usuario/AI-Youtube-Shorts-Generator/discussions)
- 📧 Email: seu-email@exemplo.com

---

**Boa sorte! 🚀**
