# 📸 GUIA COMPLETO - COMO ADICIONAR MEMES

## 🎯 **VISÃO GERAL**

O MemeDetector V4 usa **Template Matching** = compara frames do vídeo com imagens dos seus memes.

---

## 📋 **PASSO A PASSO COMPLETO**

### **1. PREPARAR PASTA**

Criar estrutura:
```
meme_templates/
  └── (vazio - você vai adicionar aqui)

hud_profiles/
  └── (vazio - será gerado automaticamente)
```

---

### **2. CALIBRAR HUD DO JOGO (1x por jogo)**

```bash
python calibrate_hud.py input/cs2_gameplay.mp4 --game cs2
```

Resultado:
- `hud_profiles/cs2_hud.json` (regiões a ignorar)
- `hud_profiles/cs2_hud_visualization.jpg` (ver o que foi detectado)

---

### **3. TIRAR PRINTS DOS MEMES**

#### **Método:**
1. Assistir live antiga no VLC/OBS
2. Pausar quando meme aparecer
3. **Windows + Shift + S** (ferramenta de recorte)
4. Selecionar **APENAS** o meme + margem 10px
5. Salvar em `meme_templates/`

#### **Tamanho:**
- ✅ Recortar apenas o meme (300x250px ~ 500x400px)
- ❌ NÃO a tela toda (1920x1080)

#### **Formato:**
- ✅ PNG
- ❌ NÃO JPG

#### **Nome:**
```
bob_esponja_tres_dias.png
silvio_santos_bixa.png
chaves_ai_que_burro.png
```

---

### **4. CRIAR meme_config.json**

Em `meme_templates/meme_config.json`:

```json
{
  "bob_esponja_tres_dias.png": {
    "description": "Bob Esponja - Três dias depois",
    "position": "top_left",
    "min_match": 0.75
  },
  "silvio_santos_bixa.png": {
    "description": "Silvio Santos - Você é homem ou bixa",
    "position": "bottom_right",
    "min_match": 0.80
  },
  "chaves_ai_que_burro.png": {
    "description": "Chaves - Ai que burro",
    "position": "top_right",
    "min_match": 0.85
  }
}
```

**min_match:**
- 0.70 = Menos rigoroso (detecta mesmo com pequenas diferenças)
- 0.75 = Balanceado (recomendado)
- 0.85 = Muito rigoroso (só detecta match perfeito)

---

### **5. TESTAR**

```bash
python Components/MemeDetector.py input/live.mp4 cs2
```

Resultado esperado:
```
✅ 5 templates carregados
✅ Perfil de HUD carregado
🎭 bob_esponja_tres_dias detectado em 125.0s (match: 0.82)
🎭 silvio_santos_bixa detectado em 380.0s (match: 0.79)
✅ 15 memes detectados
```

---

## 📐 **EXEMPLO VISUAL**

### **❌ ERRADO: Tela toda**
```
┌─────────────────────────────────────┐
│ [MEME]        (gameplay)       HUD  │
│                                     │ 1920x1080
│                                     │
└─────────────────────────────────────┘
```

### **✅ CERTO: Só o meme**
```
┌───────────┐
│   [MEME]  │ 400x300
└───────────┘
```

---

## 🎮 **FLUXO COMPLETO**

```
1. Calibrar HUD (1x por jogo)
   python calibrate_hud.py input/cs2.mp4 --game cs2
   
2. Tirar 10 prints de memes
   - Pausar live
   - Windows + Shift + S
   - Recortar só o meme
   - Salvar em meme_templates/
   
3. Criar meme_config.json
   - Adicionar entrada para cada meme
   
4. Testar
   python Components/MemeDetector.py input/live.mp4 cs2
   
5. Ajustar min_match se necessário
   - Detectou pouco? Diminuir para 0.70
   - Detectou muito? Aumentar para 0.85
```

---

## ⚙️ **AJUSTES FINOS**

### **Se detectar POUCOS memes:**
- Diminuir `min_match` para 0.70
- Adicionar mais variações do mesmo meme
- Verificar se HUD não está cobrindo meme

### **Se detectar MUITOS falsos positivos:**
- Aumentar `min_match` para 0.85
- Recalibrar HUD (cobrir mais áreas)
- Usar templates mais específicos

### **Se HUD foi detectado como meme:**
- Recalibrar com: `python calibrate_hud.py --duration 600`
- Duração maior = detecção mais precisa

---

## 📊 **QUANTOS MEMES PRECISA?**

**Mínimo:** 5 memes (testar sistema)  
**Ideal:** 20 memes (funcionamento bom)  
**Completo:** 50+ memes (cobertura total)

**Comece com os 10 mais usados!**

---

## 💡 **DICAS**

1. ✅ Tire prints de diferentes momentos da live (iluminação varia)
2. ✅ Se meme tem animação, pegue frame do meio
3. ✅ Margem de 10px ao redor ajuda na detecção
4. ✅ PNG preserva qualidade (JPG perde)
5. ✅ Nomes sem espaços ou acentos

---

## 🆘 **TROUBLESHOOTING**

**Problema:** "Nenhum template carregado"  
**Solução:** Criar pasta `meme_templates/` e adicionar PNGs

**Problema:** "Perfil de HUD não encontrado"  
**Solução:** Rodar `calibrate_hud.py` primeiro

**Problema:** "Detectou 0 memes"  
**Solução:** Diminuir `min_match` ou verificar templates

**Problema:** "Detectou HUD como meme"  
**Solução:** Recalibrar HUD com duração maior

---

**Boa sorte! 🚀**
