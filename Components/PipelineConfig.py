# Components/PipelineConfig.py
"""
=============================================================================
CONFIGURAÇÕES POR MODO DE EXECUÇÃO
=============================================================================

O QUE FAZ:
  Retorna parâmetros diferentes conforme o modo (TEST, LIVE, INSANO):
  - MAX_SHORTS: quantos shorts gerar
  - MIN_RETENTION: score mínimo de retenção (filtro)
  - MIN_VIRAL: score mínimo viral (filtro)
  - SEGMENT_MODE: "RELAXED" para critérios mais permissivos

POR QUE EXISTE:
  Permite testar com poucos shorts (TEST) ou gerar muitos (INSANO)
  sem alterar código.

ALTERAÇÕES:
  - LIVE: MAX_SHORTS de 10 → 25 (mais shorts por live)
  - INSANO: MAX_SHORTS de 25 → 35
  - MIN_RETENTION/MIN_VIRAL reduzidos para aceitar mais segmentos

O QUE AINDA PODE SER FEITO:
  - Ler de arquivo de configuração
  - AUTO: detectar duração do vídeo e ajustar MAX_SHORTS automaticamente
  - Modo CUSTOM com parâmetros via CLI
=============================================================================
"""

def get_pipeline_config(mode="LIVE"):
    """
    Retorna dict com configuração do pipeline para o modo informado.
    """
    if mode == "TEST":
        # Poucos shorts para testes rápidos
        return {
            "MAX_SHORTS": 3,
            "MIN_RETENTION": 0,
            "MIN_VIRAL": 0,
            "SEGMENT_MODE": "RELAXED"
        }

    if mode == "LIVE":
        # Modo produção: lives 4-6h → ~25 shorts
        return {
            "MAX_SHORTS": 25,
            "MIN_RETENTION": 35,
            "MIN_VIRAL": 25,
            "SEGMENT_MODE": "RELAXED"
        }

    if mode == "INSANO":
        # Máximo de shorts (para lives muito longas)
        return {
            "MAX_SHORTS": 35,
            "MIN_RETENTION": 30,
            "MIN_VIRAL": 20,
            "SEGMENT_MODE": "RELAXED"
        }

    raise ValueError("Modo inválido. Use: TEST, LIVE ou INSANO")
