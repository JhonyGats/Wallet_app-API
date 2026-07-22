# Слой работы с базой данных: получение и обновление баланса с блокировкой
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Wallet
from decimal import Decimal
from fastapi import HTTPException
from uuid import UUID

async def get_wallet_balance(db: AsyncSession, wallet_uuid: UUID) -> Decimal:
    """Получить текущий баланс кошелька по UUID."""
    # Выполняем запрос только на поле balance, чтобы сократить передаваемые данные
    result = await db.execute(select(Wallet.balance).where(Wallet.id == wallet_uuid))
    wallet = result.scalar_one_or_none()
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

async def update_wallet_balance(db: AsyncSession, wallet_uuid: UUID, operation_type: str, amount: Decimal) -> Decimal:
    """
    Обновить баланс кошелька с учётом типа операции.
    Используется пессимистическая блокировка строки (SELECT ... FOR UPDATE),
    чтобы гарантировать корректность при конкурентных запросах
    """
    # Блокируем строку для обновления - другие транзакции будут ждать, пока мы не завершим
    stmt = select(Wallet).where(Wallet.id == wallet_uuid).with_for_update()
    result = await db.execute(stmt)
    wallet = result.scalar_one_or_none()
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Вычисляем новый баланс в зависимости от типа операции
    if operation_type == "DEPOSIT":
        new_balance = wallet.balance + amount
    else:  # WITHDRAW
        if wallet.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        new_balance = wallet.balance - amount

    # Обновляем и сохраняем
    wallet.balance = new_balance
    await db.commit()          # Фиксируем изменения в БД, при этом блокировка снимается
    await db.refresh(wallet)   # Обновляем объект из БД
    return wallet.balance