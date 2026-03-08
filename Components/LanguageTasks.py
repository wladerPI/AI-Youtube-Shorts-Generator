# Components/LanguageTasks.py
"""
=============================================================================
IDENTIFICAÇÃO DE HIGHLIGHTS - PERSONALIZADO PARA 11CLOSED
=============================================================================

✅ PERSONALIZADO COM:
- Memes específicos do canal (Bob Esponja, Silvio Santos, Chaves, etc)
- Frases que o 11closed sempre fala
- Detecção de similaridade (tolera erros de OCR)
- Marcadores [RISO] do áudio

🎭 MEMES CADASTRADOS: 50+ personagens e frases
📢 COMENTÁRIOS: 15+ frases típicas do streamer

=============================================================================
"""

import os
import json
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API"):
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API")
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️ OPENAI_API_KEY não encontrada no .env")


# =============================================================================
# BIBLIOTECA DE MEMES E FRASES DO 11CLOSED
# =============================================================================

# MEMES VISUAIS/ÁUDIO (aparecem na tela + áudio)
MEMES_11CLOSED = [
    # Bob Esponja
    "três dias depois",
    "3 dias depois",
    
    # Silvio Santos
    "mais você é homem mesmo ou é bixa",
    "você é homem ou é bixa",
    "é ta bom",
    "morre porra",
    
    # Geral
    "ai ta vendo",
    "isso é uma vergonha",
    "que vergolha hem",
    "que papelão",
    
    # Mariano (jogador)
    "olha eu não sei o que aconteceu",
    "se aconteceu eu não to sabendo",
    "não é isso que aconteceu",
    "que merda hem",
    "já tava bom",
    "diz que ia mudar para melhor",
    
    # Chaves
    "ele não faz nada",
    "deve ta bebado",
    "volta o cão arrependido",
    "mas essa é muito facil mesmo",
    "passa outra mais dificil",
    "nem doeu",
    "é uma chorofompila",
    "ai que burro",
    "da zero pra ele",
    
    # Madruga
    "reprovado",
    "ladrão",
    "minha mão ta coçando",
    "para dar uns bufete",
    "eu ja to doido para uma briga de foice",
    
    # Capitão Nascimento
    "eu ja avisei que vai dar merda",
    "vai dar merda isso",
    
    # Políticos
    "você sabe porque que o lula",
    "não te messe dedinho aqui",
    "porque esse dedinho aqui é meu",
    "o imposto é muito baixo",
    "eu não sei como que conseguiu",
    "enganar tanta gente",
    "e agora em setembro vai entrar o grosso",
    "no céu tem pão",
    
    # Geral 2
    "ele é mal e agente é mal também",
    "me dão licença eu vou cagar",
    "rachamo o zói dele de tiro",
    "enchemo o rabão dele de tiro",
    "o satanás ajuda esse demonio",
    "hoje ontem e amanhã sempre",
    "eu quero eu posso",
    "não interessa para você palhaço",
    "há morre diabo",
    
    # Memes curtos
    "ain pai para",
    "ain hihi",
    "sexo",
    "secxo",
    
    # Galo Cego
    "não nada haver irmão",
    "é ué",
    
    # Pica Pau
    "vá pro inferno",
    
    # Críticas
    "mais eu sou obrigado a falar",
    "que esse programa aqui ta uma porra",
    
    # Sargento Fahur
    "cagão",
    "esse é o tal do mula",
    
    # Diversos
    "que tristeza",
    "eu não estou suportando mais",
    "estou no limite brasil",
    
    # Dilma
    "nem quem ganhar nem perder",
    "vai ganhar ou perder",
    "vai todo mundo perder",
    "eu to saudando a mandioca",
    "e é isso que a ciência faz",
    "desda arca de noé",
    "acho uma das maiores conquistas do brasil",
    
    # Música
    "aleluia",
    
    # Expressões
    "que de mais",
    "chegrei cheguei brasil",
    "não vai não ele não vai não",
    
    # Dona Irene
    "é uma vergolha brasil",
    "só besteira",
    "meu deus",
    "eu to mentindo não tô",
    
    # Coisa do demônio
    "chama a policia",
    "é coisa de deus",
    "ai ta amarrado",
    "isso ta amarrado",
    "é coisa do demonio",
    
    # Outros
    "hum boiola",
    "hamram sei",
    "eu não ouvi o que ouvi",
    "ouvi",
    
    # William Bonner
    "boa noite boa noite",
    "boa noiti",
    
    # Meme final
    "já acabou jessica"
]

# COMENTÁRIOS TÍPICOS DO 11CLOSED (o que o streamer fala)
COMENTARIOS_11CLOSED = [
    # Acertos/Conquistas
    "má oei acertei",
    "má oei",
    "boa",
    "acertei",
    
    # Frustração
    "roubado",
    "não acredito",
    "eu não fiz isso não",
    
    # Surpresa
    "olha isso",
    "puta que pariu",
    "meu deus do ceu",
    "Tá amarrado",
    
    # Ação
    "corre corre",
    
    # Culpa
    "é culpa do pele",
    
    # Ameaça (meme)
    "eu vou encher o seu rabão de tiro",
    "vou encher de tiro"
]


def _clean_llm_json(raw: str) -> str:
    """Remove markdown ```json do retorno do LLM."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
        raw = re.sub(r"```$", "", raw).strip()
    return raw


def _check_meme_match(text: str) -> bool:
    """
    Verifica se o texto contém algum meme cadastrado.
    
    TOLERÂNCIA: Aceita similaridade parcial (para erros de OCR)
    - "tres dias depois" match "três dias depois" ✅
    - "voce e homem ou e bixa" match "você é homem ou é bixa" ✅
    """
    text_lower = text.lower()
    
    # Normalizar (remover acentos para comparação)
    normalized = text_lower
    normalized = normalized.replace('á', 'a').replace('à', 'a').replace('â', 'a').replace('ã', 'a')
    normalized = normalized.replace('é', 'e').replace('ê', 'e')
    normalized = normalized.replace('í', 'i')
    normalized = normalized.replace('ó', 'o').replace('ô', 'o').replace('õ', 'o')
    normalized = normalized.replace('ú', 'u').replace('ü', 'u')
    normalized = normalized.replace('ç', 'c')
    
    # Verificar cada meme
    for meme in MEMES_11CLOSED:
        meme_normalized = meme.lower()
        meme_normalized = meme_normalized.replace('á', 'a').replace('à', 'a').replace('â', 'a').replace('ã', 'a')
        meme_normalized = meme_normalized.replace('é', 'e').replace('ê', 'e')
        meme_normalized = meme_normalized.replace('í', 'i')
        meme_normalized = meme_normalized.replace('ó', 'o').replace('ô', 'o').replace('õ', 'o')
        meme_normalized = meme_normalized.replace('ú', 'u').replace('ü', 'u')
        meme_normalized = meme_normalized.replace('ç', 'c')
        
        # Match parcial (pelo menos 70% das palavras)
        meme_words = set(meme_normalized.split())
        text_words = set(normalized.split())
        
        if meme_words and text_words:
            overlap = len(meme_words & text_words) / len(meme_words)
            if overlap >= 0.7:  # 70% de similaridade
                return True
    
    return False


def GetHighlights(transcript_text: str, video_duration_min: float = 240):
    """
    Retorna highlights PERSONALIZADOS para o canal 11closed.
    
    MUDANÇA PRINCIPAL:
    - Prompt inclui TODOS os memes e frases específicas
    - GPT prioriza momentos com esses memes
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3
    )

    # Calcular quantos momentos pedir
    num_moments = min(60, max(30, int(video_duration_min / 4)))

    # CRIAR LISTA DE MEMES PARA O PROMPT
    memes_str = "\n".join([f"   - \"{meme}\"" for meme in MEMES_11CLOSED[:30]])  # Top 30
    comentarios_str = "\n".join([f"   - \"{com}\"" for com in COMENTARIOS_11CLOSED])

    prompt = ChatPromptTemplate.from_template(
        """
Você é editor de Shorts VIRAIS do canal 11CLOSED (gameplay sem webcam).

🎯 PRIORIDADE ABSOLUTA: MEMES E FRASES ESPECÍFICAS DO CANAL

🎭 MEMES QUE APARECEM NA TELA (procure esses textos):
{memes_list}

📢 COMENTÁRIOS TÍPICOS DO STREAMER (procure essas falas):
{comentarios_list}

🔥 TAMBÉM PROCURE POR:
- [RISO], "KKKK", "kkkkk", "hahaha"
- "caralho!", "porra!", "mano!"
- "NÃOOO!", "CONSEGUI!", "WTF"
- Qualquer VARIAÇÃO dos memes acima

⚠️ REGRAS CRÍTICAS:
1. Se encontrar QUALQUER meme da lista → PRIORIDADE MÁXIMA
2. Se tiver [RISO] + meme → PRIORIDADE ALTÍSSIMA
3. Clímax = momento exato do meme ou risada
4. NUNCA repita o mesmo timestamp
5. Distribua os momentos ao longo da live

📏 PARA CADA MOMENTO:
- Identifique o CLÍMAX (timestamp exato)
- Reason: descreva qual meme/frase encontrou

FORMATO JSON (APENAS JSON, SEM TEXTO EXTRA):
[
  {{"climax": 380.5, "reason": "meme 'três dias depois' + risada"}},
  {{"climax": 1250.0, "reason": "fala 'má oei acertei' + comemoração"}},
  {{"climax": 2100.0, "reason": "meme silvio santos 'é ta bom' + fail"}}
]

Retorne EXATAMENTE {num_moments} momentos.

TRANSCRIÇÃO (procure os memes e frases acima):
{transcript}
"""
    )

    chain = prompt | llm
    response = chain.invoke({
        "transcript": transcript_text[:120000],
        "num_moments": num_moments,
        "memes_list": memes_str,
        "comentarios_list": comentarios_str
    })

    raw = response.content
    print(f"🔍 DEBUG - Resposta do GPT (primeiros 500 chars):")
    print(raw[:500])
    
    cleaned = _clean_llm_json(raw)

    try:
        moments = json.loads(cleaned)
    except Exception as e:
        print(f"❌ Erro ao parsear JSON: {e}")
        print(f"Raw: {raw[:500]}")
        return []

    # PÓS-PROCESSAMENTO
    valid_clips = []
    seen_timestamps = set()
    
    for m in moments:
        try:
            # Pegar clímax
            if "climax" in m:
                climax = float(m["climax"])
            elif "punchline" in m:
                climax = float(m["punchline"])
            else:
                continue
            
            # Evitar duplicatas
            if climax in seen_timestamps:
                continue
            seen_timestamps.add(climax)
            
            # Verificar se reason menciona meme conhecido
            reason = m.get("reason", "")
            has_known_meme = _check_meme_match(reason)
            
            # DURAÇÃO baseada no tipo
            if has_known_meme:
                duration = 70  # Memes precisam de mais contexto
            elif "riso" in reason.lower() or "kkkk" in reason.lower():
                duration = 60
            elif "fail" in reason.lower():
                duration = 75
            elif "clutch" in reason.lower():
                duration = 90
            else:
                duration = 60
            
            # Calcular start/end (40% antes, 60% depois)
            start = max(0, climax - (duration * 0.4))
            end = climax + (duration * 0.6)
            
            # Score maior para memes conhecidos
            score = 1.5 if has_known_meme else 1.0
            
            valid_clips.append({
                "start": start,
                "end": end,
                "reason": reason,
                "score": score,
                "has_meme": has_known_meme
            })
            
        except (KeyError, ValueError, TypeError) as e:
            continue

    # Ordenar por score (memes primeiro) e depois por timestamp
    valid_clips = sorted(valid_clips, key=lambda x: (-x["score"], x["start"]))
    
    print(f"✅ {len(valid_clips)} highlights encontrados")
    print(f"   🎭 {sum(1 for c in valid_clips if c['has_meme'])} com memes conhecidos")
    
    return valid_clips


# =============================================================================
# FUNÇÃO PARA ADICIONAR NOVOS MEMES
# =============================================================================

def add_custom_meme(meme_text: str):
    """
    Adiciona novo meme à biblioteca.
    
    USO:
    from Components.LanguageTasks import add_custom_meme
    add_custom_meme("novo meme aqui")
    """
    if meme_text.lower() not in [m.lower() for m in MEMES_11CLOSED]:
        MEMES_11CLOSED.append(meme_text.lower())
        print(f"✅ Meme adicionado: {meme_text}")
        
        # Salvar em arquivo
        memes_file = "profiles/lives_do_11closed/custom_memes.txt"
        os.makedirs("profiles/lives_do_11closed", exist_ok=True)
        with open(memes_file, 'a', encoding='utf-8') as f:
            f.write(f"{meme_text}\n")
    else:
        print(f"⚠️ Meme já existe: {meme_text}")


# =============================================================================
# CARREGAR MEMES CUSTOMIZADOS (se existirem)
# =============================================================================

def _load_custom_memes():
    """Carrega memes adicionais do arquivo de perfil."""
    memes_file = "profiles/lives_do_11closed/custom_memes.txt"
    if os.path.exists(memes_file):
        with open(memes_file, 'r', encoding='utf-8') as f:
            for line in f:
                meme = line.strip()
                if meme and meme not in MEMES_11CLOSED:
                    MEMES_11CLOSED.append(meme)

# Carregar na inicialização
_load_custom_memes()


"""
=============================================================================
COMO ADICIONAR MAIS MEMES NO FUTURO
=============================================================================

OPÇÃO 1: Editar este arquivo
- Adicione na lista MEMES_11CLOSED (linha ~50)
- Ou na lista COMENTARIOS_11CLOSED (linha ~150)

OPÇÃO 2: Usar função add_custom_meme()
```python
from Components.LanguageTasks import add_custom_meme
add_custom_meme("novo meme aqui")
add_custom_meme("outra frase")
```

OPÇÃO 3: Editar arquivo de texto
- Abra: profiles/lives_do_11closed/custom_memes.txt
- Adicione um meme por linha
- Será carregado automaticamente

=============================================================================
"""
