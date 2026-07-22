# Pydantic-схемы для валидации запросов и сериализации ответов
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum

# Перечисление типов операций
class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

# Схема для тела запроса на операцию пополнение/снятие
class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(..., gt=0, decimal_places=2)  # сумма > 0, не более 2 знаков после запятой

# Схема ответа с балансом
class WalletResponse(BaseModel):
    balance: Decimal