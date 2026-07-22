FROM python:3.11-slim

WORKDIR /app

# Устанавливаем netcat для проверки доступности порта
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаем с ожиданием готовности БД
CMD ["sh", "-c", "while ! nc -z db 5432; do echo \"Waiting for db...\"; sleep 1; done; alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]