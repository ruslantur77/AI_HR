import os
import requests

API_KEY = os.getenv("OPENROUTER_API_KEY", "api-key")
URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

questions = (
'''
1. Опишите процесс выявления и формализации требований для автоматизации проверок мошенничества в кредитных заявках, с которыми вы работали в Raiffeisenbank.
2. Какие методологии управления проектами (Agile/Scrum, Waterfall, Kanban) вы применяли в последних проектах и как участвовали в планировании спринтов?
'''
)

messages = [
    {
        "role": "system",
        "content": f"""Ты - AI HR специалист, который проводит техническое собеседование с кандидатом. Используй эти вопросы для скрининга:

{questions}

ИНСТРУКЦИЯ:
1. Задавай кандидату вопросы из списка выше по одному
2. Адаптируй вопросы на основе ответов кандидата, углубляйся в интересные темы
3. После всех вопросов заверши собеседование
4. После завершения собеседования сформируй ОДИН JSON объект со следующей структурой:

{{
    "hr_feedback": "Текст обратной связи для HR с технической оценкой кандидата",
    "candidate_feedback": "Текст обратной связи для кандидата с рекомендациями",
    "status": "PASSED" или "REJECTED"
}}

ТРЕБОВАНИЯ:
- Ответ должен содержать ТОЛЬКО JSON синтаксис, без каких-либо дополнительных комментариев
- Не используй markdown форматирование (```json```)
- Все термины на английском пиши русской транслитерацией (Sberbank -> Сбербанк, Docker -> докер, Agile -> эджайл, SQL -> эскуэль и т.д.)
- status должен быть строго "PASSED" или "REJECTED"
- Оценивай как технические навыки, так и soft skills
- Будь объективным и справедливым в оценке
- Используй вопросы из предоставленного списка как основу для собеседования

ПРИМЕР ВЕРНОГО ОТВЕТА:
{{"hr_feedback": "Кандидат показал хорошие знания в области эскуэль...", "candidate_feedback": "Вы продемонстрировали уверенные навыки работы с...", "status": "PASSED"}}
"""
    }
]
print("Диалог с AI HR. Введи 'exit' для выхода.\n")

while True:
    user_text = input("YOU: ")
    if user_text.strip().lower() == "exit":
        break


    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": "deepseek/deepseek-chat-v3.1",
        "messages": messages
    }

    try:
        resp = requests.post(URL, headers=HEADERS, json=payload, timeout=60)
        if resp.ok:
            answer = resp.json()["choices"][0]["message"]["content"]
            print('AI: ' + answer, end="\n\n")


            messages.append({"role": "assistant", "content": answer})
        else:
            print("Ошибка:", resp.status_code, resp.text)
    except Exception as e:
        print("Исключение:", e)