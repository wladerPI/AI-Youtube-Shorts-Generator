# review_shorts.py
"""
=============================================================================
SISTEMA DE REVISÃO INTERATIVA DE SHORTS
=============================================================================

O QUE FAZ:
  - Lista todos os shorts gerados
  - Abre cada um no player padrão
  - Pergunta: Aprovar ou Rejeitar?
  - Aprende com suas escolhas
  - Melhora próxima execução

COMO USAR:
  python review_shorts.py

CONTROLES:
  - [Enter/y] = Aprovar
  - [n] = Rejeitar
  - [s] = Pular (não conta para aprendizado)
  - [q] = Sair

=============================================================================
"""

import os
import json
import subprocess
import platform
from profile_learning import load_profile, learn_from_feedback

def open_video(filepath):
    """Abre vídeo no player padrão do sistema."""
    system = platform.system()
    
    try:
        if system == "Windows":
            os.startfile(filepath)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", filepath])
        else:  # Linux
            subprocess.run(["xdg-open", filepath])
        return True
    except Exception as e:
        print(f"   ❌ Erro ao abrir vídeo: {e}")
        return False


def load_shorts_info():
    """Carrega informações dos shorts do ranking.json."""
    ranking_file = "rankings/ranking.json"
    
    if not os.path.exists(ranking_file):
        print("❌ Arquivo rankings/ranking.json não encontrado")
        print("   Execute run_pipeline.py primeiro!")
        return []
    
    with open(ranking_file, "r", encoding="utf-8") as f:
        shorts = json.load(f)
    
    return shorts


def review_shorts():
    """Loop principal de revisão."""
    print("=" * 60)
    print("🎬 SISTEMA DE REVISÃO DE SHORTS")
    print("=" * 60)
    
    shorts = load_shorts_info()
    
    if not shorts:
        print("❌ Nenhum short encontrado para revisar")
        return
    
    print(f"\n📊 {len(shorts)} shorts encontrados\n")
    print("Controles:")
    print("  [Enter/y] = ✅ Aprovar")
    print("  [n] = ❌ Rejeitar")
    print("  [s] = ⏭️  Pular")
    print("  [q] = 🚪 Sair")
    print("=" * 60)
    
    profile = load_profile()
    reviewed = 0
    approved = 0
    rejected = 0
    
    for idx, short in enumerate(shorts, 1):
        filepath = short["file"]
        
        if not os.path.exists(filepath):
            print(f"\n⚠️  Short {idx}/{len(shorts)}: Arquivo não encontrado")
            print(f"   {filepath}")
            continue
        
        print(f"\n{'=' * 60}")
        print(f"🎬 Short {idx}/{len(shorts)}")
        print(f"{'=' * 60}")
        print(f"📄 Arquivo: {os.path.basename(filepath)}")
        print(f"⏱️  Duração: {short.get('duration', 0):.1f}s")
        print(f"💡 Motivo: {short.get('reason', 'N/A')}")
        print(f"🏆 Score: {short.get('rank', 0):.2f}")
        print(f"📊 Viral: {short.get('viral', 0):.2f} | Retenção: {short.get('retention', 0):.2f}")
        
        # Abrir vídeo
        print("\n🎥 Abrindo vídeo...")
        if not open_video(filepath):
            continue
        
        # Aguardar decisão
        while True:
            choice = input("\n👉 Sua decisão [y/n/s/q]: ").strip().lower()
            
            if choice in ['', 'y']:
                # Aprovar
                print("   ✅ APROVADO!")
                learn_from_feedback(profile, short, approved=True)
                approved += 1
                reviewed += 1
                break
            
            elif choice == 'n':
                # Rejeitar
                print("   ❌ REJEITADO")
                learn_from_feedback(profile, short, approved=False)
                rejected += 1
                reviewed += 1
                break
            
            elif choice == 's':
                # Pular
                print("   ⏭️  Pulado (não contabilizado)")
                break
            
            elif choice == 'q':
                # Sair
                print("\n🚪 Saindo da revisão...")
                _show_summary(reviewed, approved, rejected)
                return
            
            else:
                print("   ⚠️  Opção inválida. Use: y/n/s/q")
    
    # Resumo final
    _show_summary(reviewed, approved, rejected)


def _show_summary(reviewed, approved, rejected):
    """Mostra resumo da sessão de revisão."""
    print("\n" + "=" * 60)
    print("📊 RESUMO DA REVISÃO")
    print("=" * 60)
    print(f"   Revisados: {reviewed}")
    print(f"   ✅ Aprovados: {approved}")
    print(f"   ❌ Rejeitados: {rejected}")
    
    if reviewed > 0:
        approval_rate = (approved / reviewed) * 100
        print(f"   📈 Taxa de aprovação: {approval_rate:.1f}%")
    
    print("\n💡 O sistema aprendeu com suas escolhas!")
    print("   Próxima execução será mais precisa.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        review_shorts()
    except KeyboardInterrupt:
        print("\n\n⚠️  Revisão cancelada pelo usuário")
