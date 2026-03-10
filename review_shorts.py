# review_shorts.py
"""
Sistema de revisão de shorts com aprendizado automático.
"""

import argparse
import sys
from pathlib import Path
import subprocess

# IMPORT CORRIGIDO!
from Components.ProfileManager import ProfileManagerV3


def play_video(video_path):
    """Abre vídeo no player padrão do Windows."""
    subprocess.run(['start', '', str(video_path)], shell=True)


def main():
    parser = argparse.ArgumentParser(description='Revisar shorts gerados')
    parser.add_argument('shorts_dir', type=str, help='Diretório com os shorts')
    parser.add_argument('--profile', type=str, default='default', help='Nome do perfil')
    
    args = parser.parse_args()
    
    # Validar diretório
    shorts_dir = Path(args.shorts_dir)
    if not shorts_dir.exists():
        print(f"❌ Diretório não encontrado: {shorts_dir}")
        sys.exit(1)
    
    # Listar shorts
    shorts = sorted(shorts_dir.glob('short_*.mp4'))
    
    if not shorts:
        print(f"❌ Nenhum short encontrado em: {shorts_dir}")
        sys.exit(1)
    
    print("=" * 70)
    print("📋 REVISÃO DE SHORTS")
    print("=" * 70)
    print(f"📁 Diretório: {shorts_dir}")
    print(f"🎬 Shorts: {len(shorts)}")
    print(f"👤 Perfil: {args.profile}")
    print("=" * 70)
    print("\nCOMANDOS:")
    print("  [S] = Aprovar")
    print("  [N] = Rejeitar")
    print("  [P] = Pular")
    print("  [Q] = Sair")
    print("=" * 70)
    
    # Resultados da revisão
    review_results = []
    
    for i, short_path in enumerate(shorts, 1):
        print(f"\n\n{'=' * 70}")
        print(f"SHORT {i}/{len(shorts)}: {short_path.name}")
        print("=" * 70)
        
        # Abrir vídeo
        print("🎬 Abrindo vídeo...")
        play_video(short_path)
        
        # Input do usuário
        while True:
            choice = input("\n[S]im / [N]ão / [P]ular / [Q]uit: ").strip().upper()
            
            if choice == 'S':
                print("   ✅ Aprovado!")
                review_results.append({
                    'short': short_path.name,
                    'approved': True,
                    'reason': None
                })
                break
            
            elif choice == 'N':
                print("\n❌ REJEITADO!")
                print("\nMotivos comuns:")
                print("  1. Sem contexto")
                print("  2. Áudio ruim")
                print("  3. Gameplay sem graça")
                print("  4. Muito longo")
                print("  5. Outro")
                
                reason_choice = input("\nEscolha o motivo (1-5): ").strip()
                
                reasons = {
                    '1': 'Sem contexto',
                    '2': 'Áudio ruim',
                    '3': 'Gameplay sem graça',
                    '4': 'Muito longo',
                    '5': 'Outro'
                }
                
                reason = reasons.get(reason_choice, 'Outro')
                
                review_results.append({
                    'short': short_path.name,
                    'approved': False,
                    'reason': reason
                })
                break
            
            elif choice == 'P':
                print("   ⏭️  Pulado!")
                break
            
            elif choice == 'Q':
                print("\n👋 Saindo...")
                
                if review_results:
                    # Aprender com revisões
                    print("\n📊 Aplicando aprendizado...")
                    manager = ProfileManagerV3()
                    manager.learn_from_review(args.profile, review_results)
                    print("   ✅ Perfil atualizado!")
                
                sys.exit(0)
            
            else:
                print("   ⚠️  Opção inválida!")
    
    # Revisão completa
    print("\n\n" + "=" * 70)
    print("✅ REVISÃO COMPLETA!")
    print("=" * 70)
    
    approved = sum(1 for r in review_results if r['approved'])
    rejected = len(review_results) - approved
    
    print(f"\n📊 Resultados:")
    print(f"   ✅ Aprovados: {approved}")
    print(f"   ❌ Rejeitados: {rejected}")
    
    if review_results:
        approval_rate = (approved / len(review_results)) * 100
        print(f"   📈 Taxa: {approval_rate:.1f}%")
        
        # Aprender automaticamente
        print("\n📊 Aplicando aprendizado automático...")
        manager = ProfileManagerV3()
        manager.learn_from_review(args.profile, review_results)
        print("   ✅ Perfil atualizado com sucesso!")


if __name__ == '__main__':
    main()
