# Components/ProfileManager.py
"""
=============================================================================
GERENCIADOR DE PERFIL ADAPTATIVO - lives_do_11closed
=============================================================================

🎯 OBJETIVO:
Criar e gerenciar perfil que APRENDE suas preferências ao longo do tempo.

📊 O QUE APRENDE:
- Memes recorrentes e seus textos
- Palavras-chave favoritas (KKKK, caralho, mano)
- Durações ideais de shorts
- Tipos de momento preferidos (fail > clutch > explicação)
- Padrões de gameplay (horários, jogos, estilo)

💡 COMO APRENDE:
1. Você revisa shorts gerados (review_shorts.py)
2. Aprova os bons, rejeita os ruins
3. Sistema identifica padrões nos aprovados
4. Próxima live: seleção é ajustada baseado no aprendizado

🔄 CICLO DE APRENDIZADO:
Live 1 → 40 shorts gerados → você aprova 15
         ↓
Sistema aprende: durações, palavras-chave, tipos
         ↓
Live 2 → 40 shorts gerados → você aprova 25 (67% vs 37%)
         ↓
Sistema aprende mais: memes recorrentes, contexto
         ↓
Live 3 → 40 shorts gerados → você aprova 32 (80%!)

📁 ESTRUTURA DO PERFIL:
profiles/
  lives_do_11closed/
    profile.json - Dados principais
    memes.json - Biblioteca de memes
    history.json - Histórico de reviews
    insights.txt - Relatório legível

=============================================================================
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import Counter
import statistics


class ProfileManager:
    """
    Gerenciador de perfil adaptativo para lives de gameplay.
    
    PERFIL ESPECÍFICO: lives_do_11closed
    - Gameplay sem webcam
    - Memes nos cantos
    - Humor + reações + explicações
    """
    
    def __init__(self, profile_name="lives_do_11closed"):
        """
        Inicializa gerenciador de perfil.
        
        Args:
            profile_name: Nome do perfil (nome do canal)
        """
        self.profile_name = profile_name
        self.profile_dir = Path("profiles") / profile_name
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        
        self.profile_file = self.profile_dir / "profile.json"
        self.memes_file = self.profile_dir / "memes.json"
        self.history_file = self.profile_dir / "history.json"
        
        # Carregar ou criar perfil
        self.profile = self._load_or_create_profile()
    
    def _load_or_create_profile(self):
        """
        Carrega perfil existente ou cria novo.
        
        ESTRUTURA INICIAL:
        {
          "created_at": "2026-02-15T10:30:00",
          "channel_id": "lives_do_11closed",
          "total_lives": 0,
          "total_shorts_reviewed": 0,
          "approval_rate": 0.0,
          
          "meme_library": {},
          "favorite_keywords": [],
          "optimal_duration": {"min": 45, "avg": 75, "max": 150},
          "preferred_moment_types": {},
          "gameplay_patterns": {},
          
          "learning_stats": {
            "confidence": 0.0,
            "samples_needed": 50
          }
        }
        """
        if self.profile_file.exists():
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            print(f"📂 Perfil carregado: {self.profile_name}")
            print(f"   {profile['total_lives']} lives processadas")
            print(f"   {profile['total_shorts_reviewed']} shorts revisados")
            print(f"   Taxa de aprovação: {profile['approval_rate']*100:.1f}%")
            return profile
        else:
            print(f"📂 Criando novo perfil: {self.profile_name}")
            return {
                "created_at": datetime.now().isoformat(),
                "channel_id": self.profile_name,
                "total_lives": 0,
                "total_shorts_reviewed": 0,
                "approved_count": 0,
                "rejected_count": 0,
                "approval_rate": 0.0,
                
                # Biblioteca de memes recorrentes
                "meme_library": {},
                
                # Palavras-chave que aparecem em shorts aprovados
                "favorite_keywords": [],
                
                # Durações ideais baseadas em aprovações
                "optimal_duration": {
                    "min": 45,
                    "avg": 75,
                    "max": 150
                },
                
                # Tipos de momento preferidos
                "preferred_moment_types": {
                    "fail": 0.25,
                    "rizada": 0.25,
                    "clutch": 0.20,
                    "rage": 0.15,
                    "explicacao": 0.15
                },
                
                # Padrões de gameplay
                "gameplay_patterns": {
                    "games_played": [],
                    "peak_humor_times": [],
                    "avg_memes_per_hour": 0
                },
                
                # Estatísticas de aprendizado
                "learning_stats": {
                    "confidence": 0.0,  # 0.0-1.0
                    "samples_needed": 50,  # Precisa 50 reviews para boa confiança
                    "last_updated": datetime.now().isoformat()
                }
            }
    
    def save(self):
        """Salva perfil em disco."""
        self.profile["learning_stats"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Perfil salvo: {self.profile_name}")
    
    def start_new_live(self):
        """Registra início de processamento de nova live."""
        self.profile["total_lives"] += 1
        self.save()
        print(f"🎮 Live #{self.profile['total_lives']} iniciada")
    
    def learn_from_review(self, short_info, approved):
        """
        Aprende com feedback de revisão.
        
        Args:
            short_info: Dict com dados do short
                {
                  "duration": 65.3,
                  "reason": "fail épico + KKKK",
                  "transcription": "texto completo...",
                  "meme_events": [...],
                  "start": 100.0,
                  "end": 165.3
                }
            approved: True se aprovado, False se rejeitado
        
        O QUE ACONTECE:
        1. Atualiza contadores
        2. Extrai palavras-chave
        3. Atualiza durações ideais
        4. Identifica tipo de momento
        5. Registra memes presentes
        6. Recalcula preferências
        """
        self.profile["total_shorts_reviewed"] += 1
        
        if approved:
            self.profile["approved_count"] += 1
            self._learn_from_approved(short_info)
        else:
            self.profile["rejected_count"] += 1
            self._learn_from_rejected(short_info)
        
        # Recalcular taxa de aprovação
        total = self.profile["total_shorts_reviewed"]
        self.profile["approval_rate"] = self.profile["approved_count"] / total
        
        # Recalcular confiança do sistema
        self._update_confidence()
        
        # Salvar
        self.save()
        
        # Log de aprendizado
        self._log_learning_event(short_info, approved)
    
    def _learn_from_approved(self, short_info):
        """
        Aprende padrões de shorts APROVADOS.
        
        EXTRAI:
        - Palavras-chave no reason
        - Duração (atualiza média)
        - Tipo de momento
        - Memes presentes
        - Horário da live (se disponível)
        """
        # 1. PALAVRAS-CHAVE
        reason = short_info.get("reason", "").lower()
        keywords = self._extract_keywords(reason)
        
        # Adicionar às palavras favoritas (com contador)
        for keyword in keywords:
            self.profile["favorite_keywords"].append(keyword)
        
        # Manter apenas top 20 mais frequentes
        keyword_counter = Counter(self.profile["favorite_keywords"])
        self.profile["favorite_keywords"] = [
            word for word, count in keyword_counter.most_common(20)
        ]
        
        # 2. DURAÇÃO IDEAL
        duration = short_info.get("duration", 0)
        if duration > 0:
            self._update_optimal_duration(duration, approved=True)
        
        # 3. TIPO DE MOMENTO
        moment_type = self._classify_moment_type(reason)
        if moment_type:
            # Aumentar peso desse tipo
            current = self.profile["preferred_moment_types"].get(moment_type, 0.20)
            self.profile["preferred_moment_types"][moment_type] = min(current + 0.02, 1.0)
            # Normalizar (soma deve ser 1.0)
            self._normalize_moment_types()
        
        # 4. MEMES
        meme_events = short_info.get("meme_events", [])
        for meme in meme_events:
            meme_id = meme.get("meme_id")
            meme_text = meme.get("text", "")
            
            if meme_id and meme_text:
                if meme_id not in self.profile["meme_library"]:
                    self.profile["meme_library"][meme_id] = {
                        "text": meme_text,
                        "appearances": 0,
                        "approved_count": 0,
                        "approval_rate": 0.0
                    }
                
                self.profile["meme_library"][meme_id]["appearances"] += 1
                self.profile["meme_library"][meme_id]["approved_count"] += 1
                
                # Recalcular taxa
                meme_data = self.profile["meme_library"][meme_id]
                meme_data["approval_rate"] = meme_data["approved_count"] / meme_data["appearances"]
    
    def _learn_from_rejected(self, short_info):
        """
        Aprende padrões de shorts REJEITADOS.
        
        OBJETIVO:
        - Identificar o que NÃO funciona
        - Evitar durações muito curtas/longas
        - Diminuir peso de tipos de momento ruins
        """
        # 1. DURAÇÃO
        duration = short_info.get("duration", 0)
        if duration > 0:
            self._update_optimal_duration(duration, approved=False)
        
        # 2. TIPO DE MOMENTO (diminuir peso)
        reason = short_info.get("reason", "").lower()
        moment_type = self._classify_moment_type(reason)
        if moment_type:
            current = self.profile["preferred_moment_types"].get(moment_type, 0.20)
            self.profile["preferred_moment_types"][moment_type] = max(current - 0.01, 0.05)
            self._normalize_moment_types()
        
        # 3. MEMES (registrar mas não aumentar peso)
        meme_events = short_info.get("meme_events", [])
        for meme in meme_events:
            meme_id = meme.get("meme_id")
            if meme_id and meme_id in self.profile["meme_library"]:
                self.profile["meme_library"][meme_id]["appearances"] += 1
                
                # Recalcular taxa
                meme_data = self.profile["meme_library"][meme_id]
                meme_data["approval_rate"] = meme_data["approved_count"] / meme_data["appearances"]
    
    def _extract_keywords(self, text):
        """
        Extrai palavras-chave relevantes de um texto.
        
        PALAVRAS RELEVANTES:
        - Emoções: kkkk, fail, rage, wtf
        - Ações: clutch, morreu, ganhou
        - Intensificadores: épico, insano, hilário
        """
        relevant_words = [
            'kkkk', 'kkk', 'fail', 'clutch', 'épico', 'insano', 
            'rage', 'rizada', 'meme', 'wtf', 'caraca', 'porra', 
            'caralho', 'mano', 'vitória', 'derrota', 'bug', 
            'glitch', 'hilário', 'engraçado', 'morreu', 'ganhou'
        ]
        
        words = text.lower().split()
        keywords = [w for w in words if w in relevant_words]
        return keywords
    
    def _classify_moment_type(self, reason):
        """
        Classifica tipo de momento baseado no reason.
        
        Returns:
            "fail", "rizada", "clutch", "rage", "explicacao" ou None
        """
        reason = reason.lower()
        
        if any(word in reason for word in ['fail', 'morreu', 'erro']):
            return 'fail'
        elif any(word in reason for word in ['kkkk', 'kkk', 'riso', 'rizada', 'engraçado', 'hilário']):
            return 'rizada'
        elif any(word in reason for word in ['clutch', 'vitória', 'ganhou', 'consegui']):
            return 'clutch'
        elif any(word in reason for word in ['rage', 'raiva', 'porra', 'caralho']):
            return 'rage'
        elif any(word in reason for word in ['explicação', 'explica', 'ensina']):
            return 'explicacao'
        
        return None
    
    def _update_optimal_duration(self, duration, approved):
        """
        Atualiza faixa de duração ideal baseado em feedback.
        
        LÓGICA:
        - Se aprovado: ajustar min/max para incluir essa duração
        - Se rejeitado: afastar min/max dessa duração
        """
        current_min = self.profile["optimal_duration"]["min"]
        current_avg = self.profile["optimal_duration"]["avg"]
        current_max = self.profile["optimal_duration"]["max"]
        
        if approved:
            # Expandir range para incluir
            if duration < current_min:
                self.profile["optimal_duration"]["min"] = int((current_min * 0.7 + duration * 0.3))
            elif duration > current_max:
                self.profile["optimal_duration"]["max"] = int((current_max * 0.7 + duration * 0.3))
            
            # Atualizar média (gradual)
            self.profile["optimal_duration"]["avg"] = int((current_avg * 0.9 + duration * 0.1))
        
        else:
            # Rejeitado - afastar
            if duration < 60:
                # Muito curto - aumentar mínimo
                self.profile["optimal_duration"]["min"] = min(current_min + 3, 60)
            elif duration > 150:
                # Muito longo - diminuir máximo
                self.profile["optimal_duration"]["max"] = max(current_max - 5, 120)
    
    def _normalize_moment_types(self):
        """Normaliza pesos dos tipos de momento para somar 1.0."""
        total = sum(self.profile["preferred_moment_types"].values())
        if total > 0:
            for moment_type in self.profile["preferred_moment_types"]:
                self.profile["preferred_moment_types"][moment_type] /= total
    
    def _update_confidence(self):
        """
        Atualiza confiança do sistema baseado em quantidade de samples.
        
        CONFIANÇA:
        - 0-10 reviews: 0.0-0.2 (baixa)
        - 10-30 reviews: 0.2-0.5 (média)
        - 30-50 reviews: 0.5-0.8 (boa)
        - 50+ reviews: 0.8-1.0 (alta)
        """
        total = self.profile["total_shorts_reviewed"]
        
        if total < 10:
            confidence = total / 50
        elif total < 30:
            confidence = 0.2 + ((total - 10) / 100)
        elif total < 50:
            confidence = 0.4 + ((total - 30) / 50)
        else:
            confidence = min(0.8 + ((total - 50) / 200), 1.0)
        
        self.profile["learning_stats"]["confidence"] = round(confidence, 2)
    
    def _log_learning_event(self, short_info, approved):
        """Registra evento de aprendizado no histórico."""
        if not self.history_file.exists():
            history = []
        else:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "approved": approved,
            "duration": short_info.get("duration", 0),
            "reason": short_info.get("reason", ""),
            "meme_count": len(short_info.get("meme_events", []))
        }
        
        history.append(event)
        
        # Manter apenas últimos 200 eventos
        if len(history) > 200:
            history = history[-200:]
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def get_selection_preferences(self):
        """
        Retorna preferências atuais para usar na seleção de clips.
        
        Returns:
            dict com preferências para ajustar seleção
        
        USO NO PIPELINE:
        ```python
        profile = ProfileManager.load("lives_do_11closed")
        prefs = profile.get_selection_preferences()
        
        # Usar em LanguageTasks.py para ajustar prompt
        # Usar em SegmentSelectorLLM.py para filtrar clips
        ```
        """
        return {
            "favorite_keywords": self.profile["favorite_keywords"][:10],
            "optimal_duration": self.profile["optimal_duration"],
            "preferred_types": self.profile["preferred_moment_types"],
            "top_memes": self._get_top_memes(limit=5),
            "confidence": self.profile["learning_stats"]["confidence"],
            "approval_rate": self.profile["approval_rate"]
        }
    
    def _get_top_memes(self, limit=5):
        """Retorna memes com maior taxa de aprovação."""
        memes = self.profile["meme_library"]
        
        # Filtrar memes com pelo menos 2 aparições
        qualified = {
            meme_id: data for meme_id, data in memes.items()
            if data["appearances"] >= 2
        }
        
        # Ordenar por approval_rate
        sorted_memes = sorted(
            qualified.items(),
            key=lambda x: x[1]["approval_rate"],
            reverse=True
        )
        
        return [
            {
                "meme_id": meme_id,
                "text": data["text"],
                "approval_rate": data["approval_rate"]
            }
            for meme_id, data in sorted_memes[:limit]
        ]
    
    def generate_insights_report(self):
        """
        Gera relatório legível de insights aprendidos.
        
        Salva em: profiles/lives_do_11closed/insights.txt
        """
        report = []
        report.append("=" * 70)
        report.append(f"RELATÓRIO DE INSIGHTS - {self.profile_name}")
        report.append("=" * 70)
        report.append("")
        
        # Estatísticas gerais
        report.append("📊 ESTATÍSTICAS GERAIS:")
        report.append(f"   Lives processadas: {self.profile['total_lives']}")
        report.append(f"   Shorts revisados: {self.profile['total_shorts_reviewed']}")
        report.append(f"   Taxa de aprovação: {self.profile['approval_rate']*100:.1f}%")
        report.append(f"   Confiança do sistema: {self.profile['learning_stats']['confidence']*100:.0f}%")
        report.append("")
        
        # Palavras-chave favoritas
        if self.profile["favorite_keywords"]:
            report.append("🔑 PALAVRAS-CHAVE MAIS COMUNS EM SHORTS APROVADOS:")
            keyword_counter = Counter(self.profile["favorite_keywords"])
            for word, count in keyword_counter.most_common(10):
                report.append(f"   - {word}: {count} vezes")
            report.append("")
        
        # Duração ideal
        opt_dur = self.profile["optimal_duration"]
        report.append("⏱️  DURAÇÃO IDEAL:")
        report.append(f"   Mínimo: {opt_dur['min']}s")
        report.append(f"   Média: {opt_dur['avg']}s")
        report.append(f"   Máximo: {opt_dur['max']}s")
        report.append("")
        
        # Tipos de momento preferidos
        report.append("🎭 TIPOS DE MOMENTO PREFERIDOS:")
        sorted_types = sorted(
            self.profile["preferred_moment_types"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for moment_type, weight in sorted_types:
            report.append(f"   - {moment_type}: {weight*100:.1f}%")
        report.append("")
        
        # Top memes
        top_memes = self._get_top_memes(limit=10)
        if top_memes:
            report.append("🎭 MEMES MAIS APROVADOS:")
            for meme in top_memes:
                report.append(f"   - \"{meme['text']}\" ({meme['approval_rate']*100:.0f}% aprovação)")
            report.append("")
        
        # Recomendações
        report.append("💡 RECOMENDAÇÕES:")
        if self.profile["learning_stats"]["confidence"] < 0.5:
            report.append("   ⚠️  Ainda precisa de mais reviews para alta confiança")
            needed = 50 - self.profile['total_shorts_reviewed']
            report.append(f"   Revise mais {needed} shorts para melhorar aprendizado")
        else:
            report.append("   ✅ Sistema tem boa confiança nas preferências")
            report.append("   Continue revisando para aprimorar ainda mais")
        
        report.append("")
        report.append("=" * 70)
        
        # Salvar
        insights_file = self.profile_dir / "insights.txt"
        with open(insights_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report))
        
        print(f"📄 Relatório de insights salvo em: {insights_file}")
        
        return "\n".join(report)


# =============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# =============================================================================

def load_profile(profile_name="lives_do_11closed"):
    """Carrega perfil existente."""
    return ProfileManager(profile_name)


def create_profile(profile_name):
    """Cria novo perfil."""
    manager = ProfileManager(profile_name)
    manager.save()
    return manager


# =============================================================================
# SCRIPT DE TESTE
# =============================================================================

if __name__ == "__main__":
    """
    Teste standalone do ProfileManager.
    
    USO:
    python Components/ProfileManager.py
    """
    print("=" * 70)
    print("TESTE DO PROFILE MANAGER")
    print("=" * 70)
    
    # Criar/carregar perfil
    profile = load_profile("lives_do_11closed")
    
    # Simular review de alguns shorts
    print("\n📝 Simulando reviews...")
    
    # Short 1: Aprovado
    profile.learn_from_review({
        "duration": 65.3,
        "reason": "fail épico + KKKK + rage",
        "meme_events": [
            {"meme_id": "meme_001", "text": "KKKK ELE MORREU"}
        ]
    }, approved=True)
    
    # Short 2: Rejeitado (muito curto)
    profile.learn_from_review({
        "duration": 25.0,
        "reason": "riso leve",
        "meme_events": []
    }, approved=False)
    
    # Short 3: Aprovado
    profile.learn_from_review({
        "duration": 78.5,
        "reason": "clutch insano + vitória + VAMOOO",
        "meme_events": [
            {"meme_id": "meme_002", "text": "ÉPICO"}
        ]
    }, approved=True)
    
    print("\n✅ Reviews simulados")
    
    # Mostrar preferências
    print("\n📊 PREFERÊNCIAS ATUAIS:")
    prefs = profile.get_selection_preferences()
    print(f"   Keywords favoritas: {prefs['favorite_keywords']}")
    print(f"   Duração ideal: {prefs['optimal_duration']}")
    print(f"   Taxa de aprovação: {prefs['approval_rate']*100:.1f}%")
    
    # Gerar relatório
    print("\n📄 Gerando relatório de insights...")
    report = profile.generate_insights_report()
    print(report)
    
    print("\n✅ Teste completo!")


"""
=============================================================================
INTEGRAÇÃO COM O PIPELINE
=============================================================================

1. NO INÍCIO DO run_pipeline.py:
```python
from Components.ProfileManager import load_profile

# Carregar perfil
profile = load_profile("lives_do_11closed")
profile.start_new_live()

# Usar preferências na seleção
prefs = profile.get_selection_preferences()
```

2. PASSAR PREFERÊNCIAS PARA LanguageTasks.py:
```python
highlights = GetHighlights(
    transcript_text,
    video_duration_min=video_duration_min,
    profile_preferences=prefs  # NOVO parâmetro
)
```

3. APÓS GERAR SHORTS, INTEGRAR COM review_shorts.py:
```python
# Revisar e aprender
approved, rejected = review_shorts_interactive()
for short in approved:
    profile.learn_from_review(short, approved=True)
for short in rejected:
    profile.learn_from_review(short, approved=False)

# Salvar perfil atualizado
profile.save()
```

4. GERAR RELATÓRIO APÓS CADA LIVE:
```python
profile.generate_insights_report()
```

=============================================================================
"""
