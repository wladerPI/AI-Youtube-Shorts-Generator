# 📝 CHANGELOG

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

---

## [3.0.0] - 2026-03-10 🎉

### 🚀 **LANÇAMENTO VERSÃO 3.0 - SISTEMA PROFISSIONAL COMPLETO**

### ✨ Adicionado

#### **Otimização de Vídeo (VideoOptimizer)**
- Remove silêncios automático (>1 segundo)
- Acelera vídeo 1.2x-1.3x (configurável)
- Normalização de áudio profissional
- Mantém sincronia perfeita áudio/vídeo

#### **Legendas Profissionais (SubtitleGenerator)**
- Word-level timing com precisão de milissegundos
- PT-BR nativo
- Exportação .SRT + .ASS
- Múltiplos estilos: default, hormozi, mrbeast, gaming
- Quebra inteligente de linhas
- CapCut-ready

#### **Movimento de Câmera (SmartCropper)**
- Detecção de memes por TEXTO (sem GPU!)
- Movimento suave para esquerda/direita
- Retorna ao centro automaticamente
- Viável em CPU (sem processamento frame-by-frame)

#### **ProfileManager V3**
- Configurações avançadas por perfil
- Keywords personalizadas para highlight
- Velocidade de vídeo configurável
- Estilo de legendas configurável
- Remoção de silêncio on/off
- Movimento de câmera on/off
- Aprendizado mais robusto

### 🔧 Melhorado

- **Pipeline completo integrado** (7 passos)
- **Imports corrigidos** após renomeação de arquivos
- **Estrutura de código limpa** (removidos 20 arquivos duplicados)
- **Documentação completa** atualizada

### 🐛 Corrigido

- **Shorts sem áudio** (VerticalCropper agora usa ffmpeg)
- **Whisper travando** (processamento em chunks de 30 min)
- **API OpenAI inválida** (correção de .env)
- **Imports quebrados** após renomeações

### 📚 Documentação

- Novo `QUICKSTART.md` - Guia rápido
- Atualizado `README.md` - Features V3
- Novo `CHANGELOG.md` - Este arquivo
- Atualizado `USAGE.md` - Novos comandos

---

## [2.0.0] - 2026-03-08

### ✨ Adicionado

#### **Sistema de Aprendizado**
- ProfileManager V2 com multi-perfil
- Sistema de revisão interativo (review_shorts.py)
- Aprendizado automático após revisão
- Thresholds adaptativos

#### **Detecção de Memes**
- MemeScorer com 79 memes configurados
- Detecção por texto (palavras-chave)
- Sistema de pontuação 2-3x maior para memes
- meme_config.json com configurações

#### **Validação de Qualidade**
- TranscriptionValidator
- Score de qualidade 0-100
- Alertas de transcrição ruim

### 🔧 Melhorado

- ClipSelector V2 com priorização de memes
- ContextAnalyzer com GPT-4
- AudioAnalyzer com detecção de risadas
- Pipeline V2 profissional

---

## [1.0.0] - 2026-02-15

### ✨ Primeira Versão Funcional

#### **Pipeline Básico**
- Transcrição com Whisper (PT-BR)
- Análise de áudio básica
- Análise de contexto com GPT
- Seleção de clips
- Renderização vertical 9:16

#### **Componentes**
- AudioAnalyzer (básico)
- ContextAnalyzer (básico)
- ClipSelector (básico)
- VerticalCropper (básico)
- ProfileManager (básico)

### 🐛 Problemas Conhecidos

- ❌ Shorts sem áudio (corrigido em V2.0.1)
- ❌ Whisper trava em vídeos longos (corrigido em V2.0.2)
- ❌ Sem aprendizado automático (adicionado em V2.0.0)

---

## [0.1.0] - 2025-12-10

### ✨ Protótipo Inicial

- Prova de conceito básica
- Transcrição manual
- Seleção manual de clips
- Sem automação

---

## 📌 Legenda

- 🚀 **Lançamento** - Nova versão major
- ✨ **Adicionado** - Novas features
- 🔧 **Melhorado** - Melhorias em features existentes
- 🐛 **Corrigido** - Bug fixes
- ⚠️ **Depreciado** - Features que serão removidas
- ❌ **Removido** - Features removidas
- 📚 **Documentação** - Mudanças na documentação

---

## 🔮 Próximas Versões

### [3.1.0] - Planejado
- Upload automático (YouTube/TikTok/Instagram)
- Thumbnails com IA
- Analytics integrado

### [4.0.0] - Futuro
- Multi-formato (16:9, 1:1, 9:16)
- Face tracking avançado
- B-roll automático
- Música de fundo automática
