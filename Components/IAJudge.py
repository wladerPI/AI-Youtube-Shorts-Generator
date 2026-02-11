import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def judge_retention_with_ai(summary: dict):
    prompt = f"""
Avalie a chance de retenção de um short.

Dados:
{json.dumps(summary, indent=2)}

Responda APENAS em JSON:
{{
  "decision": "PUBLICAR | DESCARTAR | RERENDER",
  "confidence": 0-100,
  "reason": "curto"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return json.loads(response.choices[0].message.content)
