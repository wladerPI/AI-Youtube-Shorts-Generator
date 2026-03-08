# apply_learning.py
"""
Script simples para aplicar aprendizado de reviews ao perfil.

USO:
python apply_learning.py output/shorts_20260308_033405/reviews_lives_do_11closed.json
"""

import sys
from pathlib import Path
from Components.ProfileManager_V2 import load_profile

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python apply_learning.py <arquivo_reviews.json>")
        print("\nExemplo:")
        print("  python apply_learning.py output/shorts_20260308_033405/reviews_lives_do_11closed.json")
        sys.exit(1)
    
    reviews_file = Path(sys.argv[1])
    
    if not reviews_file.exists():
        print(f"❌ Arquivo não encontrado: {reviews_file}")
        sys.exit(1)
    
    # Extrair nome do perfil do arquivo
    profile_name = reviews_file.stem.replace('reviews_', '')
    
    print(f"📚 Aplicando aprendizado...")
    print(f"   Arquivo: {reviews_file.name}")
    print(f"   Perfil: {profile_name}")
    print()
    
    # Carregar perfil e aprender
    profile = load_profile(profile_name)
    profile.learn_from_reviews(reviews_file)
    
    print()
    print("=" * 70)
    profile.print_statistics()
    print("=" * 70)
    
    print("\n✅ Aprendizado aplicado com sucesso!")
    print(f"\n📝 PRÓXIMA LIVE:")
    print(f"   python run_pipeline_PROFESSIONAL_V2.py input/nova_live.mp4 10 --profile {profile_name}")
