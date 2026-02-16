# profile_learning.py
"""
=============================================================================
SISTEMA DE PERFIL ADAPTATIVO - APRENDE SEU ESTILO
=============================================================================

O QUE FAZ:
  - Aprende quais shorts você aprova/rejeita
  - Identifica seus memes, frases, padrões favoritos
  - Melhora a seleção a cada execução
  - Salva em profile.json

COMO USAR:
  1. Execute review_shorts.py após gerar shorts
  2. Aprove/rejeite cada short
  3. O sistema aprende automaticamente
  4. Próxima execução será melhor!

=============================================================================
"""

import json
import os
from datetime import datetime
from collections import Counter

PROFILE_FILE = "profile.json"


def load_profile():
    """Carrega perfil existente ou cria novo."""
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "created_at": datetime.now().isoformat(),
            "total_reviews": 0,
            "approved_count": 0,
            "rejected_count": 0,
            "favorite_phrases": [],  # Frases que aparecem em shorts aprovados
            "avoid_phrases": [],     # Frases em shorts rejeitados
            "favorite_reasons": [],  # Tipos de momentos preferidos
            "optimal_duration": {"min": 45, "max": 120},  # Durações favoritas
            "feedback_history": []
        }


def save_profile(profile):
    """Salva perfil no arquivo."""
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    print(f"✅ Perfil salvo em {PROFILE_FILE}")


def learn_from_feedback(profile, short_info, approved):
    """
    Aprende com feedback do usuário.
    
    Args:
        profile: Dicionário do perfil
        short_info: Info do short (duration, reason, transcription)
        approved: True se aprovado, False se rejeitado
    """
    profile["total_reviews"] += 1
    
    if approved:
        profile["approved_count"] += 1
        _learn_positive(profile, short_info)
    else:
        profile["rejected_count"] += 1
        _learn_negative(profile, short_info)
    
    # Registrar histórico
    profile["feedback_history"].append({
        "timestamp": datetime.now().isoformat(),
        "approved": approved,
        "duration": short_info.get("duration", 0),
        "reason": short_info.get("reason", "")
    })
    
    # Manter apenas últimas 100 reviews
    if len(profile["feedback_history"]) > 100:
        profile["feedback_history"] = profile["feedback_history"][-100:]
    
    save_profile(profile)


def _learn_positive(profile, short_info):
    """Aprende com short aprovado."""
    # Adicionar motivo aos favoritos
    reason = short_info.get("reason", "").lower()
    if reason:
        profile["favorite_reasons"].append(reason)
    
    # Extrair palavras-chave do motivo
    keywords = _extract_keywords(reason)
    profile["favorite_phrases"].extend(keywords)
    
    # Atualizar duração ótima
    duration = short_info.get("duration", 0)
    if duration > 0:
        _update_optimal_duration(profile, duration, approved=True)


def _learn_negative(profile, short_info):
    """Aprende com short rejeitado."""
    # Adicionar motivo aos evitados
    reason = short_info.get("reason", "").lower()
    if reason:
        keywords = _extract_keywords(reason)
        profile["avoid_phrases"].extend(keywords)
    
    # Atualizar duração (evitar muito curtos/longos se rejeitados)
    duration = short_info.get("duration", 0)
    if duration > 0:
        _update_optimal_duration(profile, duration, approved=False)


def _extract_keywords(text):
    """Extrai palavras-chave importantes de um texto."""
    # Palavras relevantes para gaming/humor
    relevant_words = [
        "kkkk", "fail", "clutch", "épico", "insano", "rage",
        "rizada", "meme", "wtf", "caraca", "porra", "caralho",
        "vitória", "derrota", "bug", "glitch", "susto", "reação"
    ]
    
    words = text.lower().split()
    keywords = [w for w in words if w in relevant_words]
    return keywords


def _update_optimal_duration(profile, duration, approved):
    """Atualiza faixa de duração ótima baseado em feedback."""
    if approved:
        # Se aprovado, ajustar para incluir essa duração
        current_min = profile["optimal_duration"]["min"]
        current_max = profile["optimal_duration"]["max"]
        
        # Ajustar min/max gradualmente
        if duration < current_min:
            profile["optimal_duration"]["min"] = int((current_min + duration) / 2)
        elif duration > current_max:
            profile["optimal_duration"]["max"] = int((current_max + duration) / 2)
    else:
        # Se rejeitado, evitar essa faixa
        if duration < 60:
            # Muito curto - aumentar mínimo
            profile["optimal_duration"]["min"] = max(45, profile["optimal_duration"]["min"] + 5)
        elif duration > 150:
            # Muito longo - diminuir máximo
            profile["optimal_duration"]["max"] = min(180, profile["optimal_duration"]["max"] - 10)


def get_profile_preferences():
    """
    Retorna preferências do perfil para usar na seleção de shorts.
    
    Returns:
        Dict com preferências aprendidas
    """
    profile = load_profile()
    
    # Contar frases favoritas mais comuns
    favorite_counter = Counter(profile.get("favorite_phrases", []))
    top_favorites = [word for word, count in favorite_counter.most_common(10)]
    
    # Contar motivos favoritos
    reason_counter = Counter(profile.get("favorite_reasons", []))
    top_reasons = [reason for reason, count in reason_counter.most_common(5)]
    
    return {
        "favorite_keywords": top_favorites,
        "favorite_types": top_reasons,
        "optimal_duration": profile.get("optimal_duration", {"min": 45, "max": 120}),
        "approval_rate": profile["approved_count"] / max(1, profile["total_reviews"]),
        "total_reviews": profile["total_reviews"]
    }


def generate_custom_prompt_suffix():
    """
    Gera sufixo personalizado para o prompt do GPT baseado no perfil.
    
    Returns:
        String com instruções personalizadas
    """
    prefs = get_profile_preferences()
    
    if prefs["total_reviews"] < 5:
        # Ainda não tem dados suficientes
        return ""
    
    suffix = "\n\n🎯 PREFERÊNCIAS APRENDIDAS DO USUÁRIO:\n"
    
    if prefs["favorite_keywords"]:
        suffix += f"- Palavras-chave favoritas: {', '.join(prefs['favorite_keywords'])}\n"
    
    if prefs["favorite_types"]:
        suffix += f"- Tipos de momento preferidos: {', '.join(prefs['favorite_types'])}\n"
    
    optimal = prefs["optimal_duration"]
    suffix += f"- Duração ideal: {optimal['min']}-{optimal['max']}s\n"
    suffix += f"- Taxa de aprovação atual: {prefs['approval_rate']*100:.1f}%\n"
    
    suffix += "\nPRIORIZE momentos que se encaixem nessas preferências!"
    
    return suffix


if __name__ == "__main__":
    # Exemplo de uso
    profile = load_profile()
    print("📊 Status do Perfil:")
    print(f"   Total de reviews: {profile['total_reviews']}")
    print(f"   Aprovados: {profile['approved_count']}")
    print(f"   Rejeitados: {profile['rejected_count']}")
    
    if profile['total_reviews'] > 0:
        prefs = get_profile_preferences()
        print(f"\n✨ Preferências Aprendidas:")
        print(f"   Keywords favoritas: {prefs['favorite_keywords']}")
        print(f"   Duração ótima: {prefs['optimal_duration']}")
        print(f"   Taxa de aprovação: {prefs['approval_rate']*100:.1f}%")
