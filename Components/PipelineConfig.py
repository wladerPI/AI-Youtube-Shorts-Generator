# Components/PipelineConfig.py
"""
=============================================================================
CONFIGURAÇÕES POR MODO DO PIPELINE
=============================================================================

ALTERAÇÕES NESTA VERSÃO:
  - LIVE: 35 shorts (era 25) - melhor para lives de 5h
  - INSANO: 50 shorts (era 35) - máximo absoluto
  - TEST: mantido em 5 para testes rápidos

=============================================================================
"""

def get_pipeline_config(mode="INSANO"):
    """
    Retorna configurações baseadas no modo selecionado.
    
    Args:
        mode: "TEST" | "LIVE" | "INSANO"
    
    Returns:
        dict com MAX_SHORTS, MIN_RETENTION, MIN_VIRAL
    """
    configs = {
        "TEST": {
            "MAX_SHORTS": 5,        # Apenas 5 shorts para testes rápidos
            "MIN_RETENTION": 0.3,   # Aceita qualquer coisa
            "MIN_VIRAL": 0.2
        },
        "LIVE": {
            "MAX_SHORTS": 35,  # Deixa gerar MUITOS shorts     # CORRIGIDO: 35 shorts para lives de 5h (~1 a cada 8.5min)
            "MIN_RETENTION": 0.5,   # Qualidade média-alta
            "MIN_VIRAL": 0.4
        },
        "INSANO": {
            "MAX_SHORTS": 50,       # Máximo absoluto - para lives muito longas
            "MIN_RETENTION": 0.4,   # Aceita mais shorts
            "MIN_VIRAL": 0.3
        }
    }
    
    return configs.get(mode, configs["LIVE"])
