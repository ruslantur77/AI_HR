import requests
import os

cv = 'резюме'
requirements ='требования'

API_KEY = os.getenv("OPENROUTER_API_KEY", "api-key")
URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def generate_screening_questions(requirements, cv):
    system_prompt = """Ты — опытный технический рекрутер. На основе резюме кандидата и требований вакансии сгенерируй 10-15 вопросов для технического скрининга.

Вопросы должны быть:
1. Конкретными и основанными на опыте кандидата
2. Охватывать ключевые технологии из требований
3. Включать вопросы о методологиях работы
4. Содержать ситуационные вопросы
5. Быть релевантными именно этому кандидату

Верни только список вопросов, без лишних комментариев."""

    user_prompt = f"""
На основе этих требований к вакансии:
{requirements}

И резюме этого кандидата:
{cv}

Сгенерируй 10-15 конкретных вопросов для технического скринингового собеседования.
"""

    payload = {
        "model": "deepseek/deepseek-chat-v3.1",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }

    try:
        resp = requests.post(URL, headers=HEADERS, json=payload, timeout=60)
        if resp.ok:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            return f"Ошибка при генерации вопросов: {resp.status_code}"
    except Exception as e:
        return f"Исключение при генерации вопросов: {e}"