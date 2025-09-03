# AI_HR

## Установка переменных окружения

Создайте файл `.env` в корне проекта и заполните его, пример:

```env
GLADIA_API_KEY="<YOUR_API_KEY>"
OPENROUTER_API_KEY="<YOUR_API_KEY>"
DB_URL="sqlite+aiosqlite:///./data.db"
ALGORITHM="HS256"
SECRET_KEY="<YOUR_SECRET_KEY>"
ACCESS_TOKEN_EXPIRE_MINUTES="15"
REFRESH_TOKEN_EXPIRE_DAYS="7"

ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="string"
````

SECRET_KEY генерируется командой `openssl rand -base64 32`. Пример - `b66LtTr+Feyd2lr+DuHJlZwzP5vwn+JbCFRXS1wrVzc=`


## Применение миграций

```bash
alembic upgrade head
```

## Запуск приложения

```bash
uvicorn main:app --reload --log-level info
```

Интерфейс будет доступен на [http://localhost:8000/](http://localhost:8000/)

## Интерактивная документация API

[http://localhost:8000/docs](http://localhost:8000/docs)

Можно залогиниться как администратор по данным `ADMIN_EMAIL` и `ADMIN_PASSWORD`, указанным в переменных окружения до применения миграций.