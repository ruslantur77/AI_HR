from typing import TypedDict

import httpx

from config import config

API_KEY = config.OPENROUTER_API_KEY
URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
SYSTEM_INSTRUCTIONS = "Ты полезный ассистент. Отвечаешь в стиле человека без форматирвоания, специальных символов,\
      разметки, кода и так далее. Ответ - 1-2 предложения. Все английские слова ты пишешь на русском.\
          Например Google - 'Гугл', docker - 'докер' "
MODEL = "deepseek/deepseek-chat-v3.1"


class MessageType(TypedDict):
    role: str
    content: str


def get_system_instruction(content: str) -> MessageType:
    return {"role": "system", "content": content}


async def get_response(
    src_messages: list[MessageType], user_text: str, max_tokens: int = 100
) -> tuple[list[MessageType], str]:
    if len(src_messages) == 0:
        messages: list[MessageType] = [get_system_instruction(SYSTEM_INSTRUCTIONS)]
    else:
        messages = src_messages.copy()

    messages.append({"role": "user", "content": user_text})
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(URL, headers=HEADERS, json=payload, timeout=60)
        res.raise_for_status()
        answer: dict = res.json()["choices"][0]["message"]
        messages.append({"role": answer["role"], "content": answer["content"]})

    return messages, answer["content"]
