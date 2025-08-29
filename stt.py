import requests

api_key = "api-key"
audio_file_path = "001.mp3"

url = "https://api.gladia.io/audio/text/audio-transcription/"

headers = {
    "x-gladia-key": api_key,
}

with open(audio_file_path, "rb") as f:
    files = {
        "audio": (audio_file_path, f, "audio/wav")
    }
    response = requests.post(url, headers=headers, files=files)

if response.status_code == 200:
    result = response.json()

    full_text = ""
    for segment in result["prediction"]:
        full_text += segment["transcription"] + " "
    

    full_text = full_text.strip()
    print(full_text)
    
else:
    print("Ошибка:", response.status_code, response.text)