# AI_HR


## Запуск

Необходимо указать Gladia API ключ в файле `.env` в корне проекта.


```
GLADIA_API_KEY="<YOUR_API_KEY>"
```


```bash
uvicorn main:app --reload --log-level info
```

Интерфейс будет доступен на `localhost:8000/`