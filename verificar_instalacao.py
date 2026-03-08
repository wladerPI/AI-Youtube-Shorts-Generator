# verificar_instalacao.py
"""
=============================================================================
VERIFICADOR DE INSTALAÇÃO - AUDITORIA COMPLETA
=============================================================================

Verifica se TUDO está instalado e configurado corretamente antes de rodar.

USO:
python verificar_instalacao.py

=============================================================================
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Verifica versão do Python."""
    print("\n1️⃣ VERIFICANDO PYTHON...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} (precisa 3.8+)")
        return False

def check_dependencies():
    """Verifica dependências Python."""
    print("\n2️⃣ VERIFICANDO DEPENDÊNCIAS...")
    
    deps = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'whisper': 'openai-whisper',
        'langchain': 'langchain',
        'langchain_openai': 'langchain-openai',
        'dotenv': 'python-dotenv'
    }
    
    all_ok = True
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - instalar: pip install {package}")
            all_ok = False
    
    return all_ok

def check_structure():
    """Verifica estrutura de pastas."""
    print("\n3️⃣ VERIFICANDO ESTRUTURA...")
    
    required = [
        'Components/',
        'Components/LanguageTasks.py',
        'Components/MemeDetectorPro.py',
        'Components/ProfileManager.py',
        'Render/',
        'Render/VerticalCropper.py',
        'Render/CameraControllerV2.py',
        'meme_templates/',
        'meme_templates/meme_config.json',
        'run_pipeline_FINAL.py'
    ]
    
    all_ok = True
    for item in required:
        path = Path(item)
        if path.exists():
            print(f"   ✅ {item}")
        else:
            print(f"   ❌ {item} - FALTANDO!")
            all_ok = False
    
    return all_ok

def check_templates():
    """Verifica templates de memes."""
    print("\n4️⃣ VERIFICANDO TEMPLATES...")
    
    templates_dir = Path('meme_templates')
    if not templates_dir.exists():
        print("   ❌ Pasta meme_templates/ não existe!")
        return False
    
    pngs = list(templates_dir.glob('*.png'))
    print(f"   📊 {len(pngs)} imagens PNG encontradas")
    
    if len(pngs) == 0:
        print("   ❌ Nenhum template encontrado!")
        return False
    elif len(pngs) < 10:
        print("   ⚠️ Poucos templates (ideal: 50+)")
    else:
        print(f"   ✅ {len(pngs)} templates OK")
    
    # Verificar nomes sem acentos
    problematic = []
    for png in pngs:
        name = png.name
        if any(c in name for c in 'áàâãéêíóôõúüç'):
            problematic.append(name)
    
    if problematic:
        print(f"   ⚠️ {len(problematic)} arquivos COM ACENTOS:")
        for p in problematic[:5]:
            print(f"      - {p}")
        if len(problematic) > 5:
            print(f"      ... e mais {len(problematic)-5}")
        return False
    else:
        print("   ✅ Nomes sem acentos")
    
    return True

def check_config():
    """Verifica meme_config.json."""
    print("\n5️⃣ VERIFICANDO CONFIGURAÇÃO...")
    
    config_file = Path('meme_templates/meme_config.json')
    if not config_file.exists():
        print("   ❌ meme_config.json não existe!")
        return False
    
    try:
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"   ✅ JSON válido ({len(config)} memes configurados)")
        
        # Verificar estrutura
        for meme_name, meme_data in list(config.items())[:3]:
            if 'position' in meme_data and 'min_match' in meme_data:
                print(f"      ✅ {meme_name}: {meme_data['position']}")
            else:
                print(f"      ⚠️ {meme_name}: falta position ou min_match")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro ao ler config: {e}")
        return False

def check_env():
    """Verifica .env."""
    print("\n6️⃣ VERIFICANDO VARIÁVEIS DE AMBIENTE...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("   ❌ .env não existe!")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
    
    if 'OPENAI_API_KEY' in content:
        print("   ✅ OPENAI_API_KEY configurada")
        return True
    else:
        print("   ❌ OPENAI_API_KEY não encontrada no .env")
        return False

def check_ffmpeg():
    """Verifica ffmpeg."""
    print("\n7️⃣ VERIFICANDO FFMPEG...")
    
    import subprocess
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   ✅ {version_line}")
            return True
        else:
            print("   ❌ ffmpeg não funciona corretamente")
            return False
    except FileNotFoundError:
        print("   ❌ ffmpeg não instalado!")
        print("      Baixe em: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"   ❌ Erro ao verificar ffmpeg: {e}")
        return False

def main():
    """Executa todas as verificações."""
    print("=" * 70)
    print("VERIFICAÇÃO DE INSTALAÇÃO - AUDITORIA COMPLETA")
    print("=" * 70)
    
    checks = [
        ("Python", check_python_version),
        ("Dependências", check_dependencies),
        ("Estrutura", check_structure),
        ("Templates", check_templates),
        ("Config", check_config),
        ("Env", check_env),
        ("FFmpeg", check_ffmpeg)
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO:")
    print("=" * 70)
    
    all_ok = True
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if not result:
            all_ok = False
    
    print("=" * 70)
    
    if all_ok:
        print("\n🎉 TUDO OK! Pronto para rodar:")
        print("   python run_pipeline_FINAL.py input/seu_video.mp4")
    else:
        print("\n⚠️ CORRIJA OS PROBLEMAS ACIMA ANTES DE RODAR!")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
