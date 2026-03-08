# 📖 Guia de Uso Completo

Como usar todas as funcionalidades do AI-Youtube-Shorts-Generator.

---

## 📋 **Índice**

- [Workflow Básico](#workflow-básico)
- [Comandos Principais](#comandos-principais)
- [Revisar Shorts](#revisar-shorts)
- [Sistema de Perfis](#sistema-de-perfis)
- [Opções Avançadas](#opções-avançadas)
- [Dicas e Boas Práticas](#dicas-e-boas-práticas)

---

## 🚀 **Workflow Básico**

### **Passo 1: Preparar o Vídeo**

Coloque sua live na pasta `input/`:

```
input/minha_live.mp4
```

**Recomendações:**
- Formato: MP4, MKV, AVI
- Resolução: Mínimo 720p
- Áudio: Obrigatório
- Duração: Qualquer (otimizado para 1-4 horas)

### **Passo 2: Ativar Ambiente**

```bash
# Windows
cd /d F:\AI-Shorts\AI-Youtube-Shorts-Generator
.venv\Scripts\activate

# Linux/macOS
cd ~/AI-Youtube-Shorts-Generator
source .venv/bin/activate
```

### **Passo 3: Processar Live**

```bash
python run_pipeline_PROFESSIONAL_V2.py input/minha_live.mp4 10 --profile meu_canal
```

**Parâmetros:**
- `input/minha_live.mp4` - Caminho do vídeo
- `10` - Número de shorts a gerar
- `--profile meu_canal` - Nome do seu perfil

**Tempo estimado:**
- Live de 1h: ~20-30 minutos
- Live de 2h: ~40-60 minutos
- Live de 4h: ~90-120 minutos

### **Passo 4: Revisar Shorts**

```bash
python review_shorts.py output/shorts_20260308_033405/ --profile meu_canal
```

**Interface:**
```
[1/10] short_001.mp4
==================================================
🎬 Vídeo abre automaticamente

   Avaliação [S/N/P/Q]: 
```

**Teclas:**
- `S` - Aprovar ✅
- `N` - Rejeitar ❌
- `P` - Pular
- `Q` - Sair

**Sistema aprende automaticamente ao final!**

### **Passo 5: Upload**

Shorts aprovados estão em:
```
output/shorts_20260308_033405/
├─ short_001.mp4 ✅
├─ short_003.mp4 ✅
└─ short_005.mp4 ✅
```

Faça upload no YouTube/TikTok/Instagram!

---

## ⚙️ **Comandos Principais**

### **1. Processar Live**

```bash
# Básico (10 shorts)
python run_pipeline_PROFESSIONAL_V2.py input/live.mp4 10 --profile meu_canal

# Gerar mais shorts
python run_pipeline_PROFESSIONAL_V2.py input/live.mp4 20 --profile meu_canal

# Gerar menos shorts
python run_pipeline_PROFESSIONAL_V2.py input/live.mp4 5 --profile meu_canal
```

### **2. Revisar Shorts**

```bash
python review_shorts.py output/shorts_XXXXXX/ --profile meu_canal
```

### **3. Ver Estatísticas do Perfil**

```bash
python -c "from Components.ProfileManager_V2 import load_profile; p = load_profile('meu_canal'); p.print_statistics()"
```

### **4. Listar Todos os Perfis**

```bash
python -c "from Components.ProfileManager_V2 import list_profiles; list_profiles()"
```

---

## 📝 **Revisar Shorts**

### **Como Funciona:**

1. **Vídeo abre automaticamente** no player padrão
2. **Você assiste** e decide
3. **Digita S ou N**
4. **Se N**: escolhe motivo da rejeição

### **Motivos de Rejeição:**

```
1. Sem graça       - Momento não engraçado
2. Sem contexto    - Clip começa/termina mal
3. Momento ruim    - Não é interessante
4. Áudio ruim      - Problemas de áudio
5. Corte errado    - Timing do corte ruim
6. Outro           - Outros motivos
```

### **Exemplo de Sessão:**

```
[1/10] short_001.mp4
   Avaliação: S ✅

[2/10] short_002.mp4
   Avaliação: N
   Motivos: 1,5 (sem graça + corte errado) ❌

[3/10] short_003.mp4
   Avaliação: S ✅

...

✅ REVISÃO COMPLETA!
📊 Aprovados: 7/10 (70%)

🧠 APLICANDO APRENDIZADO...
   ✅ Sistema aprendeu!
   Próxima live terá melhores resultados!
```

---

## 👤 **Sistema de Perfis**

### **Para Que Servem?**

Cada perfil aprende preferências individuais:
- Tipo de momentos que você gosta
- Duração ideal dos shorts
- Quanto de meme é necessário
- Thresholds otimizados

### **Criar Novo Perfil:**

```bash
# Processar primeira live com novo perfil
python run_pipeline_PROFESSIONAL_V2.py input/live.mp4 10 --profile canal_novo
```

Perfil é criado automaticamente!

### **Múltiplos Perfis:**

```bash
# Seu canal principal
python run_pipeline_PROFESSIONAL_V2.py input/live1.mp4 10 --profile meu_canal

# Canal de um amigo
python run_pipeline_PROFESSIONAL_V2.py input/live2.mp4 10 --profile canal_amigo

# Canal de testes
python run_pipeline_PROFESSIONAL_V2.py input/teste.mp4 5 --profile testes
```

Cada perfil mantém:
- Taxa de aprovação independente
- Thresholds próprios
- Histórico de lives
- Motivos de rejeição

### **Ver Perfil Específico:**

```bash
python -c "from Components.ProfileManager_V2 import load_profile; p = load_profile('meu_canal'); p.print_statistics()"
```

**Saída:**
```
📊 ESTATÍSTICAS DO PERFIL: meu_canal
   Lives processadas: 5
   Shorts gerados: 50
   Shorts revisados: 45
   Taxa de aprovação: 75.6%

   🎯 Thresholds otimizados:
      Min score: 3.8
      Min meme score: 3.2
      Duração: 60-180s
```

---

## ⚙️ **Opções Avançadas**

### **Personalizar Número de Shorts:**

```bash
# Gerar 50 shorts
python run_pipeline_PROFESSIONAL_V2.py input/live.mp4 50 --profile meu_canal

# Gerar apenas 3 (para teste rápido)
python run_pipeline_PROFESSIONAL_V2.py input/teste.mp4 3 --profile teste
```

### **Processar Múltiplas Lives:**

```bash
# Criar script batch (Windows)
@echo off
python run_pipeline_PROFESSIONAL_V2.py input/live1.mp4 10 --profile meu_canal
python run_pipeline_PROFESSIONAL_V2.py input/live2.mp4 10 --profile meu_canal
python run_pipeline_PROFESSIONAL_V2.py input/live3.mp4 10 --profile meu_canal
```

```bash
# Script shell (Linux/macOS)
#!/bin/bash
for live in input/*.mp4; do
    python run_pipeline_PROFESSIONAL_V2.py "$live" 10 --profile meu_canal
done
```

### **Revisar Apenas Alguns Shorts:**

```bash
# Apertar Q para sair a qualquer momento
# Sistema aprende com o que você já revisou!
```

---

## 💡 **Dicas e Boas Práticas**

### **1. Primeiras Lives:**

- ✅ Comece com 10 shorts
- ✅ Revise TODOS na primeira live
- ✅ A partir da 3ª live, taxa sobe para 70%+

### **2. Memes:**

- ✅ Configure bem o `meme_config.json`
- ✅ Use palavras que você REALMENTE fala
- ✅ Evite palavras genéricas demais

**Exemplo ruim:**
```json
"description": "sim"  ❌ Muito genérico
```

**Exemplo bom:**
```json
"description": "olha o cachorro caramelo latindo au au"  ✅ Específico
```

### **3. Qualidade do Áudio:**

- ✅ Remover ruído de fundo antes
- ✅ Usar áudio em 44.1kHz ou superior
- ✅ Evitar música muito alta sobre a voz

### **4. Duração das Lives:**

**Ideal:** 1-4 horas
- Muito curto (< 30 min): Poucos momentos
- Muito longo (> 6 horas): Processamento lento

**Solução para lives longas:**
```bash
# Cortar live em partes de 2h cada
ffmpeg -i live_longa.mp4 -t 02:00:00 -c copy parte1.mp4
ffmpeg -i live_longa.mp4 -ss 02:00:00 -t 02:00:00 -c copy parte2.mp4
```

### **5. Taxa de Aprovação:**

| Taxa | Significado |
|------|-------------|
| < 50% | Sistema ainda aprendendo |
| 50-70% | Sistema bom |
| 70-85% | Sistema ótimo! |
| > 85% | Considerar aumentar exigência |

### **6. Manutenção:**

```bash
# Limpar arquivos temporários (toda semana)
del audio_*.wav
del temp_segment_*.mp4

# Backup dos perfis (mensal)
mkdir backup_profiles
copy profiles\*.json backup_profiles\
```

---

## 🎯 **Casos de Uso**

### **Caso 1: Primeira Live**

```bash
# 1. Processar
python run_pipeline_PROFESSIONAL_V2.py input/live1.mp4 10 --profile meu_canal

# 2. Revisar TUDO (importante!)
python review_shorts.py output/shorts_XXXXX/ --profile meu_canal

# 3. Ver estatísticas
# Taxa: ~50% (normal na primeira)
```

### **Caso 2: Depois de 3 Lives**

```bash
# Sistema já aprendeu!
python run_pipeline_PROFESSIONAL_V2.py input/live4.mp4 10 --profile meu_canal

# Taxa esperada: 70%+
# Thresholds otimizados automaticamente
```

### **Caso 3: Testar Configurações**

```bash
# Usar perfil de teste
python run_pipeline_PROFESSIONAL_V2.py input/teste.mp4 5 --profile teste

# Revisar
python review_shorts.py output/shorts_XXXXX/ --profile teste

# Se gostar, usar no perfil principal
```

---

## 📞 **Precisa de Ajuda?**

- 📚 Ver: [CONFIGURATION.md](CONFIGURATION.md) - Configurações avançadas
- 🏗️ Ver: [ARCHITECTURE.md](ARCHITECTURE.md) - Como funciona
- 🐛 [Reportar problema](https://github.com/seu-usuario/AI-Youtube-Shorts-Generator/issues)

---

**Bons shorts! 🎬🚀**
