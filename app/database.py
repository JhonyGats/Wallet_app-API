# Настройка подключения к базе данных PostgreSQL с использованием асинхронного драйвера asyncpg
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Строка подключения для локальной разработки
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/wallet_db")

# Создаём асинхронный движок SQLAlchemy, echo=True выводит SQL-запросы в лог
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика сессий для асинхронной работы
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Базовый класс для моделей
Base = declarative_base()

# Зависимость FastAPI для получения сессии БД в эндпоинтах
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session