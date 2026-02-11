import json
import os
from datetime import datetime

MEMORY_DIR = "learning"
MEMORY_FILE = os.path.join(MEMORY_DIR, "memory.json")
STATS_FILE = os.path.join(MEMORY_DIR, "stats.json")


def _load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def register_short_decision(summary, ai_decision):
    """
    Salva aprendizado da IA para decisões futuras
    """

    memory = _load_json(MEMORY_FILE, [])
    stats = _load_json(STATS_FILE, {
        "APROVADO": 0,
        "DESCARTADO": 0,
        "RERENDER": 0
    })

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "viral_score": summary["viral_score"],
        "retention_score": summary.get("retention_score", 0),
        "drop_risk": summary["drop_risk"],
        "stability": summary["stability"],
        "reason": summary["reason"],
        "decision": ai_decision["decision"],
        "confidence": ai_decision.get("confidence", None)
    }

    memory.append(record)
    stats[ai_decision["decision"]] += 1

    # Limita histórico para não crescer infinito
    memory = memory[-1000:]

    _save_json(MEMORY_FILE, memory)
    _save_json(STATS_FILE, stats)
