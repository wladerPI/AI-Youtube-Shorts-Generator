# Components/ProfileManager_V2.py
"""
=============================================================================
GERENCIADOR DE PERFIS V2 - MULTI-PERFIL COM APRENDIZADO
=============================================================================

🎯 MELHORIAS:
1. Suporte a múltiplos perfis (você, outros criadores)
2. Aprendizado baseado em reviews
3. Estatísticas avançadas por perfil
4. Ajuste automático de thresholds
5. Preferências individuais

✅ EXEMPLO:
profile = load_profile("lives_do_11closed")
profile.learn_from_reviews()  # Aprende com reviews
profile.get_optimal_thresholds()  # Ajusta automaticamente

=============================================================================
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class ProfileV2:
    """Perfil de criador com aprendizado."""
    
    def __init__(self, name):
        """
        Inicializa perfil.
        
        Args:
            name: Nome do perfil
        """
        self.name = name
        self.profile_path = Path(f"profiles/{name}.json")
        self.data = self._load_or_create()
    
    def _load_or_create(self):
        """Carrega ou cria perfil."""
        if self.profile_path.exists():
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Criar novo perfil
            return {
                'name': self.name,
                'created_at': datetime.now().isoformat(),
                'lives_processadas': 0,
                'shorts_gerados': 0,
                'shorts_revisados': 0,
                'aprovados': 0,
                'rejeitados': 0,
                'taxa_aprovacao': 0.0,
                'preferences': {
                    'min_score': 3.0,
                    'min_meme_score': 2.0,
                    'min_laugh_concentration': 2,
                    'duracao_preferida': 60,
                    'duracao_min': 45,
                    'duracao_max': 240
                },
                'thresholds': {
                    'audio_energy': 0.5,
                    'spectral_flux': 1.2,
                    'meme_bonus': 2.0,
                    'laugh_bonus': 1.5
                },
                'rejection_reasons': {},
                'learned_patterns': {
                    'good_moments': [],
                    'bad_moments': []
                },
                'history': []
            }
    
    def save(self):
        """Salva perfil."""
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Perfil salvo: {self.name}")
    
    def start_new_live(self):
        """Registra início de nova live."""
        self.data['lives_processadas'] += 1
        print(f"🎮 Live #{self.data['lives_processadas']} iniciada")
    
    def add_shorts_generated(self, count):
        """Registra shorts gerados."""
        self.data['shorts_gerados'] += count
    
    def learn_from_reviews(self, reviews_file=None):
        """
        Aprende com reviews de shorts.
        
        Args:
            reviews_file: Arquivo JSON com reviews (opcional)
        """
        if reviews_file is None:
            # Procurar último arquivo de reviews
            reviews_files = sorted(Path('output').glob(f'**/reviews_{self.name}.json'))
            if not reviews_files:
                print("⚠️ Nenhum arquivo de reviews encontrado")
                return
            reviews_file = reviews_files[-1]
        
        print(f"🧠 Aprendendo com reviews: {reviews_file.name}")
        
        with open(reviews_file, 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
        
        reviews = reviews_data.get('reviews', [])
        
        # Analisar padrões
        approved_count = 0
        rejected_count = 0
        
        for review in reviews:
            if review.get('approved'):
                approved_count += 1
                # Adicionar aos momentos bons
                self.data['learned_patterns']['good_moments'].append({
                    'short_name': review['short_name'],
                    'timestamp': review['timestamp']
                })
            else:
                rejected_count += 1
                # Adicionar aos momentos ruins
                self.data['learned_patterns']['bad_moments'].append({
                    'short_name': review['short_name'],
                    'reasons': review.get('reasons', []),
                    'timestamp': review['timestamp']
                })
        
        # Atualizar estatísticas
        self.data['shorts_revisados'] += len(reviews)
        self.data['aprovados'] += approved_count
        self.data['rejeitados'] += rejected_count
        
        total = self.data['aprovados'] + self.data['rejeitados']
        if total > 0:
            self.data['taxa_aprovacao'] = (self.data['aprovados'] / total) * 100
        
        # Ajustar thresholds automaticamente
        self._adjust_thresholds()
        
        print(f"   ✅ Aprendizado concluído!")
        print(f"   Taxa de aprovação: {self.data['taxa_aprovacao']:.1f}%")
        
        self.save()
    
    def _adjust_thresholds(self):
        """Ajusta thresholds baseado em performance."""
        approval_rate = self.data['taxa_aprovacao']
        
        print(f"\n   🎯 Ajustando thresholds...")
        
        # Se taxa muito baixa = aumentar exigência
        if approval_rate < 50:
            self.data['preferences']['min_score'] += 0.5
            self.data['preferences']['min_meme_score'] += 0.5
            print(f"      ⬆️ Aumentando exigência (taxa: {approval_rate:.1f}%)")
        
        # Se taxa muito alta = diminuir exigência (buscar mais variedade)
        elif approval_rate > 85:
            self.data['preferences']['min_score'] = max(2.0, self.data['preferences']['min_score'] - 0.3)
            print(f"      ⬇️ Diminuindo exigência (taxa: {approval_rate:.1f}%)")
        
        # Ajustar baseado em motivos de rejeição
        rejection_reasons = self.data.get('rejection_reasons', {})
        
        if rejection_reasons.get('sem_graca', 0) > 3:
            # Muitos "sem graça" = aumentar exigência de memes
            self.data['preferences']['min_meme_score'] += 1.0
            print(f"      🎭 Aumentando exigência de memes")
        
        if rejection_reasons.get('sem_contexto', 0) > 3:
            # Muitos "sem contexto" = aumentar duração mínima
            self.data['preferences']['duracao_min'] = min(90, self.data['preferences']['duracao_min'] + 15)
            print(f"      ⏱️ Aumentando duração mínima")
    
    def get_optimal_thresholds(self):
        """Retorna thresholds otimizados."""
        return {
            'min_score': self.data['preferences']['min_score'],
            'min_meme_score': self.data['preferences']['min_meme_score'],
            'min_laugh_concentration': self.data['preferences']['min_laugh_concentration'],
            'duracao_min': self.data['preferences']['duracao_min'],
            'duracao_max': self.data['preferences']['duracao_max']
        }
    
    def get_statistics(self):
        """Retorna estatísticas do perfil."""
        return {
            'name': self.name,
            'lives_processadas': self.data['lives_processadas'],
            'shorts_gerados': self.data['shorts_gerados'],
            'shorts_revisados': self.data['shorts_revisados'],
            'taxa_aprovacao': self.data['taxa_aprovacao'],
            'aprovados': self.data['aprovados'],
            'rejeitados': self.data['rejeitados'],
            'created_at': self.data['created_at']
        }
    
    def print_statistics(self):
        """Imprime estatísticas."""
        print(f"\n📊 ESTATÍSTICAS DO PERFIL: {self.name}")
        print(f"   Lives processadas: {self.data['lives_processadas']}")
        print(f"   Shorts gerados: {self.data['shorts_gerados']}")
        print(f"   Shorts revisados: {self.data['shorts_revisados']}")
        print(f"   Aprovados: {self.data['aprovados']} ✅")
        print(f"   Rejeitados: {self.data['rejeitados']} ❌")
        print(f"   Taxa de aprovação: {self.data['taxa_aprovacao']:.1f}%")
        
        # Thresholds atuais
        print(f"\n   🎯 Thresholds otimizados:")
        print(f"      Min score: {self.data['preferences']['min_score']}")
        print(f"      Min meme score: {self.data['preferences']['min_meme_score']}")
        print(f"      Duração: {self.data['preferences']['duracao_min']}-{self.data['preferences']['duracao_max']}s")
        
        # Motivos de rejeição
        if self.data.get('rejection_reasons'):
            print(f"\n   📉 Principais motivos de rejeição:")
            sorted_reasons = sorted(
                self.data['rejection_reasons'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for reason, count in sorted_reasons[:3]:
                print(f"      - {reason}: {count}x")


# =============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# =============================================================================

def load_profile(name):
    """
    Carrega perfil.
    
    Args:
        name: Nome do perfil
    
    Returns:
        ProfileV2
    """
    profile = ProfileV2(name)
    
    stats = profile.get_statistics()
    print(f"📂 Perfil carregado: {name}")
    print(f"   {stats['lives_processadas']} lives processadas")
    print(f"   {stats['shorts_revisados']} shorts revisados")
    if stats['shorts_revisados'] > 0:
        print(f"   Taxa de aprovação: {stats['taxa_aprovacao']:.1f}%")
    
    return profile


def list_profiles():
    """Lista todos os perfis disponíveis."""
    profiles_dir = Path('profiles')
    
    if not profiles_dir.exists():
        print("📂 Nenhum perfil criado ainda")
        return []
    
    profile_files = list(profiles_dir.glob('*.json'))
    
    if not profile_files:
        print("📂 Nenhum perfil criado ainda")
        return []
    
    print(f"\n📂 PERFIS DISPONÍVEIS ({len(profile_files)}):")
    
    profiles = []
    for pf in profile_files:
        profile = ProfileV2(pf.stem)
        stats = profile.get_statistics()
        profiles.append(profile)
        
        print(f"\n   {stats['name']}")
        print(f"      Lives: {stats['lives_processadas']}")
        print(f"      Shorts: {stats['shorts_gerados']}")
        print(f"      Taxa aprovação: {stats['taxa_aprovacao']:.1f}%")
    
    return profiles


# =============================================================================
# COMPATIBILIDADE COM CÓDIGO ANTIGO
# =============================================================================

class Profile:
    """Wrapper para compatibilidade."""
    
    def __init__(self, name):
        self.v2 = ProfileV2(name)
        self.data = self.v2.data
    
    def save(self):
        self.v2.save()
    
    def start_new_live(self):
        self.v2.start_new_live()


# =============================================================================
# TESTE
# =============================================================================

if __name__ == "__main__":
    # Listar perfis
    list_profiles()
    
    # Carregar perfil de exemplo
    print("\n" + "=" * 70)
    profile = load_profile("lives_do_11closed")
    profile.print_statistics()
