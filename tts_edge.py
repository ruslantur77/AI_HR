import edge_tts
import asyncio

async def text_to_mp3(text, filename):
  communicate = edge_tts.Communicate(text, 'ru-RU-DmitryNeural')

  await communicate.save(filename)


text = "Привет! Это пример синтеза речи на русском языке. Я люблю eggs"
filename = 'voice.mp3'
asyncio.run(text_to_mp3(text, filename))