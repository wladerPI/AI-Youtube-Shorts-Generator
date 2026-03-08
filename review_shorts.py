# review_shorts.py
"""
=============================================================================
SISTEMA DE REVISÃO DE SHORTS - MULTI-PERFIL
=============================================================================

🎯 FUNCIONALIDADES:
1. Interface para revisar shorts gerados
2. Suporta múltiplos perfis (você, outros criadores)
3. Sistema de aprendizado por perfil
4. Estatísticas detalhadas
5. Exporta dados para ProfileManager

✅ USO:
python review_shorts.py output/shorts_20260307_014936/ --profile lives_do_11closed

=============================================================================
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import subprocess


class ShortReviewer:
    """Sistema de revisão de shorts."""
    
    def __init__(self, shorts_folder, profile_name):
        """
        Inicializa revisor.
        
        Args:
            shorts_folder: Pasta com os shorts
            profile_name: Nome do perfil
        """
        self.shorts_folder = Path(shorts_folder)
        self.profile_name = profile_name
        self.reviews = []
        
        # Carregar shorts
        self.shorts = sorted(self.shorts_folder.glob("short_*.mp4"))
        
        print("=" * 70)
        print(f"🎬 SISTEMA DE REVISÃO DE SHORTS")
        print("=" * 70)
        print(f"Pasta: {self.shorts_folder.name}")
        print(f"Perfil: {profile_name}")
        print(f"Shorts encontrados: {len(self.shorts)}")
        print("=" * 70)
    
    def review_all(self):
        """Revisa todos os shorts."""
        print("\n📝 INSTRUÇÕES:")
        print("   S = Aprovou ✅")
        print("   N = Rejeitou ❌")
        print("   P = Pular (revisar depois)")
        print("   Q = Sair")
        print()
        
        for i, short_path in enumerate(self.shorts, 1):
            print(f"\n{'=' * 70}")
            print(f"[{i}/{len(self.shorts)}] {short_path.name}")
            print(f"{'=' * 70}")
            
            # Abrir vídeo
            self._play_video(short_path)
            
            # Pedir avaliação
            while True:
                choice = input("\n   Avaliação [S/N/P/Q]: ").strip().upper()
                
                if choice == 'S':
                    self.reviews.append({
                        'short_name': short_path.name,
                        'approved': True,
                        'timestamp': datetime.now().isoformat()
                    })
                    print("   ✅ APROVADO!")
                    break
                
                elif choice == 'N':
                    # Pedir motivo
                    reasons = self._get_rejection_reasons()
                    
                    self.reviews.append({
                        'short_name': short_path.name,
                        'approved': False,
                        'reasons': reasons,
                        'timestamp': datetime.now().isoformat()
                    })
                    print("   ❌ REJEITADO!")
                    break
                
                elif choice == 'P':
                    print("   ⏭️ PULADO")
                    break
                
                elif choice == 'Q':
                    print("\n   🛑 Salvando e saindo...")
                    self._save_reviews()
                    self._apply_learning()  # APLICAR APRENDIZADO
                    return
                
                else:
                    print("   ⚠️ Opção inválida!")
        
        # Finalizar
        print(f"\n{'=' * 70}")
        print("✅ REVISÃO COMPLETA!")
        print(f"{'=' * 70}")
        
        self._save_reviews()
        self._show_statistics()
        
        # APLICAR APRENDIZADO AUTOMATICAMENTE
        self._apply_learning()
    
    def _play_video(self, video_path):
        """Abre vídeo no player padrão."""
        try:
            if sys.platform == 'win32':
                os.startfile(str(video_path))
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(video_path)])
            else:
                subprocess.run(['xdg-open', str(video_path)])
        except Exception as e:
            print(f"   ⚠️ Erro ao abrir vídeo: {e}")
            print(f"   Abra manualmente: {video_path}")
    
    def _get_rejection_reasons(self):
        """Pergunta motivos da rejeição."""
        print("\n   Por que rejeitou? (pode marcar vários)")
        print("   1. Sem graça")
        print("   2. Sem contexto")
        print("   3. Momento ruim")
        print("   4. Áudio ruim")
        print("   5. Corte errado")
        print("   6. Outro")
        
        reasons = []
        reason_map = {
            '1': 'sem_graca',
            '2': 'sem_contexto',
            '3': 'momento_ruim',
            '4': 'audio_ruim',
            '5': 'corte_errado',
            '6': 'outro'
        }
        
        choice = input("\n   Motivos (ex: 1,3,5): ").strip()
        
        for num in choice.split(','):
            num = num.strip()
            if num in reason_map:
                reasons.append(reason_map[num])
        
        return reasons if reasons else ['nao_especificado']
    
    def _save_reviews(self):
        """Salva avaliações."""
        output_file = self.shorts_folder / f"reviews_{self.profile_name}.json"
        
        data = {
            'profile_name': self.profile_name,
            'shorts_folder': str(self.shorts_folder),
            'total_shorts': len(self.shorts),
            'reviewed': len(self.reviews),
            'timestamp': datetime.now().isoformat(),
            'reviews': self.reviews
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Avaliações salvas: {output_file}")
        
        # Atualizar ProfileManager
        self._update_profile()
    
    def _update_profile(self):
        """Atualiza ProfileManager V2 com avaliações."""
        try:
            # Tentar V2 primeiro
            try:
                from Components.ProfileManager_V2 import load_profile
            except ImportError:
                from Components.ProfileManager import load_profile
            
            profile = load_profile(self.profile_name)
            
            # Adicionar reviews
            approved = sum(1 for r in self.reviews if r.get('approved'))
            rejected = sum(1 for r in self.reviews if not r.get('approved'))
            
            # Atualizar estatísticas (V2 usa profile.data)
            if hasattr(profile, 'data'):
                data = profile.data
            elif hasattr(profile, 'v2'):
                data = profile.v2.data
            else:
                print("⚠️ Perfil incompatível")
                return
            
            data['shorts_revisados'] += len(self.reviews)
            data['aprovados'] = data.get('aprovados', 0) + approved
            data['rejeitados'] = data.get('rejeitados', 0) + rejected
            
            # Calcular nova taxa
            total = data['aprovados'] + data['rejeitados']
            if total > 0:
                data['taxa_aprovacao'] = (data['aprovados'] / total) * 100
            
            # Analisar motivos de rejeição
            rejection_reasons = data.get('rejection_reasons', {})
            for review in self.reviews:
                if not review.get('approved'):
                    for reason in review.get('reasons', []):
                        rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            
            data['rejection_reasons'] = rejection_reasons
            
            profile.save()
            
            print(f"✅ Perfil '{self.profile_name}' atualizado!")
            print(f"   Taxa de aprovação: {data['taxa_aprovacao']:.1f}%")
            
        except Exception as e:
            print(f"⚠️ Erro ao atualizar perfil: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_statistics(self):
        """Mostra estatísticas da revisão."""
        if not self.reviews:
            return
        
        approved = sum(1 for r in self.reviews if r.get('approved'))
        rejected = len(self.reviews) - approved
        approval_rate = (approved / len(self.reviews)) * 100
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Revisados: {len(self.reviews)}/{len(self.shorts)}")
        print(f"   Aprovados: {approved} ✅")
        print(f"   Rejeitados: {rejected} ❌")
        print(f"   Taxa de aprovação: {approval_rate:.1f}%")
        
        # Motivos de rejeição
        if rejected > 0:
            all_reasons = []
            for r in self.reviews:
                if not r.get('approved'):
                    all_reasons.extend(r.get('reasons', []))
            
            if all_reasons:
                from collections import Counter
                reason_counts = Counter(all_reasons)
                
                print(f"\n   Principais motivos de rejeição:")
                for reason, count in reason_counts.most_common(3):
                    print(f"      - {reason}: {count}x")
    
    def _apply_learning(self):
        """Aplica aprendizado automaticamente ao perfil."""
        if not self.reviews:
            return
        
        print(f"\n{'=' * 70}")
        print("🧠 APLICANDO APRENDIZADO AO PERFIL...")
        print(f"{'=' * 70}")
        
        try:
            # Tentar V2 primeiro
            try:
                from Components.ProfileManager_V2 import load_profile
                is_v2 = True
            except ImportError:
                from Components.ProfileManager import load_profile
                is_v2 = False
            
            profile = load_profile(self.profile_name)
            
            if is_v2:
                # Usar método learn_from_reviews do V2
                reviews_file = self.shorts_folder / f"reviews_{self.profile_name}.json"
                
                if reviews_file.exists():
                    print(f"\n🔄 Analisando {len(self.reviews)} avaliações...")
                    profile.learn_from_reviews(reviews_file)
                    
                    print(f"\n📊 PERFIL ATUALIZADO:")
                    stats = profile.get_statistics()
                    print(f"   Lives processadas: {stats['lives_processadas']}")
                    print(f"   Shorts revisados: {stats['shorts_revisados']}")
                    print(f"   Taxa de aprovação: {stats['taxa_aprovacao']:.1f}%")
                    
                    # Mostrar thresholds otimizados
                    thresholds = profile.get_optimal_thresholds()
                    print(f"\n   🎯 Thresholds otimizados para próxima live:")
                    print(f"      Min score: {thresholds['min_score']:.1f}")
                    print(f"      Min meme score: {thresholds['min_meme_score']:.1f}")
                    print(f"      Duração: {thresholds['duracao_min']}-{thresholds['duracao_max']}s")
                    
                    print(f"\n✅ Sistema aprendeu! Próxima live terá melhores resultados!")
                else:
                    print(f"⚠️ Arquivo de reviews não encontrado")
            else:
                print(f"⚠️ ProfileManager V2 não disponível - aprendizado manual necessário")
                print(f"   Execute: python apply_learning.py {self.shorts_folder}/reviews_{self.profile_name}.json")
        
        except Exception as e:
            print(f"\n⚠️ Erro ao aplicar aprendizado: {e}")
            print(f"   Execute manualmente: python apply_learning.py {self.shorts_folder}/reviews_{self.profile_name}.json")


# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python review_shorts.py <pasta_shorts> [--profile nome_perfil]")
        print("\nExemplo:")
        print("  python review_shorts.py output/shorts_20260307_014936/")
        print("  python review_shorts.py output/shorts_20260307_014936/ --profile lives_do_11closed")
        sys.exit(1)
    
    shorts_folder = sys.argv[1]
    
    # Extrair nome do perfil
    profile_name = "default"
    if "--profile" in sys.argv:
        idx = sys.argv.index("--profile")
        if idx + 1 < len(sys.argv):
            profile_name = sys.argv[idx + 1]
    
    # Verificar se pasta existe
    if not os.path.exists(shorts_folder):
        print(f"❌ Pasta não encontrada: {shorts_folder}")
        sys.exit(1)
    
    # Iniciar revisão
    reviewer = ShortReviewer(shorts_folder, profile_name)
    
    try:
        reviewer.review_all()
    except KeyboardInterrupt:
        print("\n\n⚠️ Revisão interrompida!")
        reviewer._save_reviews()
        reviewer._show_statistics()
        reviewer._apply_learning()  # APLICAR APRENDIZADO
