import sherpa_onnx
from huggingface_hub import hf_hub_download
import wave

# Скачиваем нужные файлы модели
model_path = hf_hub_download(
    repo_id="csukuangfj/vits-piper-ru_RU-ruslan-medium", 
    filename="ru_RU-ruslan-medium.onnx"
)
tokens_path = hf_hub_download(
    repo_id="csukuangfj/vits-piper-ru_RU-ruslan-medium", 
    filename="tokens.txt"
)

# Создаем конфигурацию для TTS
config = sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=model_path,
            tokens=tokens_path,
            data_dir="/tmp/espeak-ng-data",  # путь к данным eSpeak NG
        ),
        num_threads=2,
        debug=False,
        provider="cpu",  # используйте "cuda" если есть GPU
    ),
    rule_fsts="",
    max_num_sentences=1,
)

# Инициализируем TTS
tts = sherpa_onnx.OfflineTts(config)

# Генерируем речь
text = "Привет, это тестовая фраза на русском языке."
audio = tts.generate(text, sid=0, speed=1.0)

# Сохраняем в WAV файл
with wave.open("output.wav", "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)  # 16-bit PCM
    f.setframerate(tts.sample_rate)
    f.writeframes(audio.samples)

print("Аудио успешно сохранено в output.wav")