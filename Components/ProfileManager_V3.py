# Components/ProfileManager_V3.py
"""
=============================================================================
PROFILE MANAGER V3 - CONFIGURAÇÕES AVANÇADAS
=============================================================================

✨ FEATURES:
- Multi-perfil com aprendizado
- Keywords personalizadas
- Estilos de legenda configuráveis
- Velocidade de vídeo configurável
- Remoção de silêncio configurável
- Movimento de câmera configurável
- Thresholds adaptativos

=============================================================================
"""

import json
from pathlib import Path
from datetime import datetime


class ProfileManagerV3:
    """Gerenciador de perfis avançado com aprendizado."""
    
    def __init__(self, profiles_dir='profiles'):
        """
        Inicializa gerenciador.
        
        Args:
            profiles_dir: Diretório dos perfis
        """
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
    
    def create_profile(self, name, config=None):
        """
        Cria novo perfil.
        
        Args:
            name: Nome do perfil
            config: Configuração inicial (opcional)
        
        Returns:
            Perfil criado
        """
        default_config = {
            'name': name,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            
            # Configurações de seleção
            'thresholds': {
                'min_score': 3.5,
                'min_audio_score': 1.0,
                'min_context_score': 1.0,
                'min_meme_score': 1.0
            },
            
            # Configurações de vídeo
            'video': {
                'speed_factor': 1.25,           # 1.0 = normal, 1.25 = 25% mais rápido
                'remove_silences': True,
                'silence_threshold': -35,        # dB
                'min_silence_duration': 1.0,     # segundos
                'camera_movement_enabled': True
            },
            
            # Configurações de legendas
            'subtitles': {
                'enabled': True,
                'style': 'default',              # default, hormozi, mrbeast, gaming
                'max_chars_per_line': 42,
                'generate_srt': True,
                'generate_ass': True
            },
            
            # Keywords personalizadas (highlight automático)
            'keywords_to_highlight': [
                'puta que pariu',
                'olha isso',
                'meu deus',
                'caralho',
                'não acredito'
            ],
            
            # Configurações de jogo (opcional)
            'game': {
                'name': None,                    # Ex: 'dreadway'
                'hud_zones': None                # Zonas de UI para evitar
            },
            
            # Histórico de aprendizado
            'learning': {
                'total_reviews': 0,
                'approved': 0,
                'rejected': 0,
                'approval_rate': 0.0,
                'rejection_reasons': {},
                'adjustments_history': []
            }
        }
        
        # Merge com config fornecida
        if config:
            profile = self._deep_merge(default_config, config)
        else:
            profile = default_config
        
        # Salvar
        self.save_profile(name, profile)
        
        return profile
    
    def load_profile(self, name):
        """
        Carrega perfil.
        
        Args:
            name: Nome do perfil
        
        Returns:
            Perfil carregado ou None
        """
        profile_path = self.profiles_dir / f"{name}.json"
        
        if not profile_path.exists():
            print(f"⚠️  Perfil '{name}' não existe. Criando novo...")
            return self.create_profile(name)
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_profile(self, name, profile):
        """
        Salva perfil.
        
        Args:
            name: Nome do perfil
            profile: Dados do perfil
        """
        profile['updated_at'] = datetime.now().isoformat()
        
        profile_path = self.profiles_dir / f"{name}.json"
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
    
    def learn_from_review(self, profile_name, review_results):
        """
        Aprende com revisão de shorts.
        
        Args:
            profile_name: Nome do perfil
            review_results: Lista de {'approved': bool, 'reason': str, 'score': float}
        """
        profile = self.load_profile(profile_name)
        
        # Atualizar estatísticas
        total = len(review_results)
        approved = sum(1 for r in review_results if r.get('approved', False))
        rejected = total - approved
        
        profile['learning']['total_reviews'] += total
        profile['learning']['approved'] += approved
        profile['learning']['rejected'] += rejected
        
        # Calcular taxa de aprovação
        total_all = profile['learning']['total_reviews']
        approved_all = profile['learning']['approved']
        
        approval_rate = (approved_all / total_all * 100) if total_all > 0 else 0
        profile['learning']['approval_rate'] = approval_rate
        
        # Contar motivos de rejeição
        for result in review_results:
            if not result.get('approved', False):
                reason = result.get('reason', 'Sem motivo')
                
                if reason not in profile['learning']['rejection_reasons']:
                    profile['learning']['rejection_reasons'][reason] = 0
                
                profile['learning']['rejection_reasons'][reason] += 1
        
        # Ajustar thresholds baseado na taxa de aprovação
        adjustment = self._calculate_threshold_adjustment(approval_rate)
        
        if adjustment != 0:
            old_threshold = profile['thresholds']['min_score']
            new_threshold = max(1.0, min(10.0, old_threshold + adjustment))
            
            profile['thresholds']['min_score'] = new_threshold
            
            # Registrar ajuste
            profile['learning']['adjustments_history'].append({
                'date': datetime.now().isoformat(),
                'approval_rate': approval_rate,
                'old_threshold': old_threshold,
                'new_threshold': new_threshold,
                'adjustment': adjustment
            })
            
            print(f"   📊 Taxa de aprovação: {approval_rate:.1f}%")
            print(f"   🎯 Threshold ajustado: {old_threshold:.1f} → {new_threshold:.1f}")
        
        # Salvar
        self.save_profile(profile_name, profile)
        
        return profile
    
    def _calculate_threshold_adjustment(self, approval_rate):
        """
        Calcula ajuste de threshold baseado na taxa de aprovação.
        
        Args:
            approval_rate: Taxa de aprovação (0-100)
        
        Returns:
            Ajuste para threshold (-1.0 a +1.0)
        """
        if approval_rate < 30:
            return -0.5  # Muito rigoroso, diminuir threshold
        elif approval_rate < 50:
            return -0.3
        elif approval_rate > 90:
            return +0.5  # Muito permissivo, aumentar threshold
        elif approval_rate > 80:
            return +0.3
        else:
            return 0  # Zona ótima (50-80%)
    
    def _deep_merge(self, base, update):
        """Merge profundo de dicionários."""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_config_summary(self, profile_name):
        """
        Retorna resumo da configuração do perfil.
        
        Args:
            profile_name: Nome do perfil
        
        Returns:
            String com resumo
        """
        profile = self.load_profile(profile_name)
        
        summary = f"""
╔══════════════════════════════════════════════════════════════════╗
║  PERFIL: {profile['name']:<54} ║
╠══════════════════════════════════════════════════════════════════╣
║  SELEÇÃO:                                                        ║
║    Min Score: {profile['thresholds']['min_score']:<43.1f} ║
║                                                                  ║
║  VÍDEO:                                                          ║
║    Velocidade: {profile['video']['speed_factor']:<41.2f}x ║
║    Remove Silêncios: {str(profile['video']['remove_silences']):<37} ║
║    Movimento de Câmera: {str(profile['video']['camera_movement_enabled']):<32} ║
║                                                                  ║
║  LEGENDAS:                                                       ║
║    Estilo: {profile['subtitles']['style']:<47} ║
║    Gera .SRT: {str(profile['subtitles']['generate_srt']):<44} ║
║    Gera .ASS: {str(profile['subtitles']['generate_ass']):<44} ║
║                                                                  ║
║  APRENDIZADO:                                                    ║
║    Reviews: {profile['learning']['total_reviews']:<46} ║
║    Taxa Aprovação: {profile['learning']['approval_rate']:<37.1f}% ║
╚══════════════════════════════════════════════════════════════════╝
"""
        
        return summary


# =============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# =============================================================================

def load_or_create_profile(name):
    """Carrega ou cria perfil."""
    manager = ProfileManagerV3()
    return manager.load_profile(name)


def update_profile_config(name, updates):
    """
    Atualiza configurações do perfil.
    
    Args:
        name: Nome do perfil
        updates: Dicionário com atualizações
    """
    manager = ProfileManagerV3()
    profile = manager.load_profile(name)
    profile = manager._deep_merge(profile, updates)
    manager.save_profile(name, profile)
    return profile
