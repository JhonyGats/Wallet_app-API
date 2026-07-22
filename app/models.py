# Описание модели данных Wallet
from sqlalchemy import Column, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base

class Wallet(Base):
    __tablename__ = "wallets"  # Имя таблицы в БД

    # UUID в качестве первичного ключа, генерируется автоматически
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Баланс с точностью до 2 знаков после запятой, по умолчанию 0.00
    balance = Column(Numeric(10, 2), nullable=False, server_default='0.00')
    # Время создания записи (заполняется сервером БД)
    created_at = Column(DateTime, server_default=func.now())
    # Время последнего обновления (обновляется автоматически при изменении)
    updated_at = Column(DateTime, onupdate=func.now())