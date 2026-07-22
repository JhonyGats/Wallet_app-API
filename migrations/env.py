# Конфигурация Alembic для выполнения миграций
import os
import sys
sys.path.append(os.getcwd())
from app.database import Base
from app.models import Wallet  # регистрация моделей

target_metadata = Base.metadata

def get_url():
    # Оригинальный URL (с asyncpg) для основного приложения
    return os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/wallet_db")

def get_sync_url():
    # Для миграций используем синхронный драйвер (psycopg2)
    return get_url().replace("+asyncpg", "")

# Далее стандартный код Alembic
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Переопределим sqlalchemy.url в конфиге на синхронный
config.set_main_option('sqlalchemy.url', get_sync_url())

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()