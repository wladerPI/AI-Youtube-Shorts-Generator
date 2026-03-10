# apply_learning.py
"""
Script para aplicar aprendizado manualmente ao perfil.
"""

import argparse
import json
from pathlib import Path

# IMPORT CORRIGIDO!
from Components.ProfileManager import ProfileManagerV3


def main():
    parser = argparse.ArgumentParser(description='Aplicar aprendizado ao perfil')
    parser.add_argument('profile', type=str, help='Nome do perfil')
    parser.add_argument('--review-file', type=str, help='Arquivo JSON com resultados da revisão')
    parser.add_argument('--show-stats', action='store_true', help='Mostrar estatísticas do perfil')
    
    args = parser.parse_args()
    
    manager = ProfileManagerV3()
    
    if args.show_stats:
        # Mostrar estatísticas
        profile = manager.load_profile(args.profile)
        
        print("=" * 70)
        print(f"📊 ESTATÍSTICAS DO PERFIL: {args.profile}")
        print("=" * 70)
        print(f"\n🎯 Threshold atual: {profile['thresholds']['min_score']:.1f}")
        print(f"\n📈 Histórico:")
        print(f"   Total de reviews: {profile['learning']['total_reviews']}")
        print(f"   Aprovados: {profile['learning']['approved']}")
        print(f"   Rejeitados: {profile['learning']['rejected']}")
        print(f"   Taxa de aprovação: {profile['learning']['approval_rate']:.1f}%")
        
        if profile['learning']['rejection_reasons']:
            print(f"\n❌ Motivos de rejeição:")
            for reason, count in profile['learning']['rejection_reasons'].items():
                print(f"   {reason}: {count}")
        
        if profile['learning']['adjustments_history']:
            print(f"\n⚙️  Histórico de ajustes:")
            for adj in profile['learning']['adjustments_history'][-5:]:  # Últimos 5
                print(f"   {adj['date'][:10]} → {adj['old_threshold']:.1f} para {adj['new_threshold']:.1f} (taxa: {adj['approval_rate']:.1f}%)")
        
        print("=" * 70)
    
    elif args.review_file:
        # Carregar arquivo de revisão
        review_file = Path(args.review_file)
        
        if not review_file.exists():
            print(f"❌ Arquivo não encontrado: {review_file}")
            return
        
        with open(review_file, 'r', encoding='utf-8') as f:
            review_results = json.load(f)
        
        print(f"📊 Aplicando aprendizado de {len(review_results)} revisões...")
        manager.learn_from_review(args.profile, review_results)
        print("✅ Perfil atualizado!")
    
    else:
        print("⚠️  Use --show-stats para ver estatísticas ou --review-file para aplicar aprendizado")


if __name__ == '__main__':
    main()
