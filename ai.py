import os
import json
import requests
import sys

if os.name == "nt":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

API_KEY   = os.getenv("OPENROUTER_API_KEY", "api-key")
URL       = "https://openrouter.ai/api/v1/chat/completions"
HEADERS   = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

messages = [{"role": "system", "content": "Ты полезный ассистент."}]
print("Диалог с OpenRouter (стриминг). Введи 'exit' для выхода.\n")

while True:
    user_text = input("> ")
    if user_text.strip().lower() == "exit":
        break

    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": "deepseek/deepseek-chat-v3.1",
        "messages": messages,
        "stream": True
    }

    try:
        resp = requests.post(URL, headers=HEADERS, json=payload, stream=True, timeout=60)
        resp.raise_for_status()

        assistant_chunk = ""
        print("assistant: ", end="", flush=True)

        for line in resp.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data = line_str[6:]
                    if data == '[DONE]':
                        break
                    try:
                        json_data = json.loads(data)
                        if 'content' in json_data['choices'][0]['delta']:
                            piece = json_data['choices'][0]['delta']['content']
                            print(piece, end='', flush=True)
                            assistant_chunk += piece
                    except json.JSONDecodeError:
                        continue

        print("\n")
        messages.append({"role": "assistant", "content": assistant_chunk})

    except Exception as e:
        print("Ошибка:", e)