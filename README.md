
# AI_HR

## 1. Подготовка окружения

### Создание файла `.env`

В корне проекта необходимо создать файл `.env` со следующим содержимым (пример):

```bash
GLADIA_API_KEY="<YOUR_API_KEY>"
OPENROUTER_API_KEY="<YOUR_API_KEY>"
DB_URL="sqlite+aiosqlite:///./data.db"
ALGORITHM="HS256"
SECRET_KEY="<YOUR_SECRET_KEY>"
ACCESS_TOKEN_EXPIRE_MINUTES="15"
REFRESH_TOKEN_EXPIRE_DAYS="7"

ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="string"

EMAIL_SENDER="your-email@example.com"
EMAIL_SENDER_PASS="your-email-password"

HOST="http://localhost:5173"

LOG_LEVEL="INFO"
```

Секретный ключ можно сгенерировать командой:

```bash
openssl rand -base64 32
```



## 2. Бэкенд

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Применение миграций

```bash
alembic upgrade head
```

### Запуск сервера

```bash
uvicorn main:app --reload --log-level info --port 8000
```

После запуска:

* API доступно на [http://localhost:8000](http://localhost:8000)
* Документация Swagger — [http://localhost:8000/docs](http://localhost:8000/docs)


## 3. Фронтенд

### Переход в каталог фронтенда

```bash
cd frontend
```

### Установка зависимостей

```bash
npm install
```

### Запуск в режиме разработки (порт 5173)

```bash
npm run dev -- --port 5173
```

Фронтенд будет доступен на [http://localhost:5173](http://localhost:5173)


## 4. Вход в систему

1. Перейти на страницу входа:
   [http://localhost:5173/login](http://localhost:5173/login)

2. Ввести логин и пароль администратора из `.env`:

   * Email: `ADMIN_EMAIL`
   * Пароль: `ADMIN_PASSWORD`

После входа будет доступен интерфейс HR.

В `.env` должны быть заполнены параметры отправителя:

```env
EMAIL_SENDER="your-email@example.com"
EMAIL_SENDER_PASS="your-email-password"
```

Эти данные используются приложением для отправки писем кандидатам.
Когда HR добавляет нового кандидата и назначает собеседование, ссылка для подключения отправляется на email кандидата с использованием учётных данных почтового аккаунта, указанного в `.env`.

Поэтому необходимо указывать реальный email и пароль/ключ приложения, иначе письма рассылаться не будут.

