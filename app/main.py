# Основной файл приложения FastAPI
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import schemas, crud
from uuid import UUID

# Создаём экземпляр приложения
app = FastAPI(title="Wallet API")

# Эндпоинт для выполнения операции (пополнение или снятие)
@app.post("/api/v1/wallets/{wallet_uuid}/operation", response_model=schemas.WalletResponse)
async def perform_operation(
    wallet_uuid: UUID,
    operation: schemas.OperationRequest,  # валидация тела запроса
    db: AsyncSession = Depends(get_db)    # внедрение сессии БД
):
    new_balance = await crud.update_wallet_balance(
        db, wallet_uuid, operation.operation_type.value, operation.amount
    )
    return schemas.WalletResponse(balance=new_balance)

# Эндпоинт для получения текущего баланса
@app.get("/api/v1/wallets/{wallet_uuid}", response_model=schemas.WalletResponse)
async def get_balance(
    wallet_uuid: UUID,
    db: AsyncSession = Depends(get_db)
):
    balance = await crud.get_wallet_balance(db, wallet_uuid)
    return schemas.WalletResponse(balance=balance)