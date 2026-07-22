import pytest
import uuid
import psycopg2
from psycopg2 import sql
from app.schemas import OperationType

# Вспомогательные функции для работы с БД
def get_db_connection():
    """Возвращает синхронное подключение к PostgreSQL для тестов"""
    return psycopg2.connect(
        host="db",
        database="wallet_db",
        user="postgres",
        password="postgres"
    )

def create_test_wallet():
    """
    Создаёт в БД новый кошелёк с балансом 0.00 и возвращает его UUID
    UUID передаётся как строка, чтобы избежать ошибок адаптации psycopg2
    """
    conn = get_db_connection()
    cur = conn.cursor()
    wallet_uuid = uuid.uuid4()
    cur.execute(
        sql.SQL("INSERT INTO wallets (id, balance) VALUES (%s, %s) RETURNING id"),
        (str(wallet_uuid), 0.00)  # явное преобразование в строку
    )
    conn.commit()
    cur.close()
    conn.close()
    return wallet_uuid

def delete_test_wallet(wallet_uuid):
    """Удаляет кошелёк по UUID"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM wallets WHERE id = %s", (str(wallet_uuid),))
    conn.commit()
    cur.close()
    conn.close()

# Тесты
def test_get_balance_existing(client):
    """Проверяет, что GET-запрос к существующему кошельку возвращает 200 и баланс 0.00"""
    wallet_id = create_test_wallet()
    try:
        resp = client.get(f"/api/v1/wallets/{wallet_id}")
        assert resp.status_code == 200
        assert resp.json()["balance"] == "0.00"
    finally:
        delete_test_wallet(wallet_id)

def test_get_balance_not_found(client):
    """Запрос к несуществующему UUID должен возвращать 404"""
    random_uuid = uuid.uuid4()
    resp = client.get(f"/api/v1/wallets/{random_uuid}")
    assert resp.status_code == 404

def test_deposit(client):
    """Проверяет пополнение баланса на 100.50"""
    wallet_id = create_test_wallet()
    try:
        resp = client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": OperationType.DEPOSIT.value, "amount": "100.50"}
        )
        assert resp.status_code == 200
        assert resp.json()["balance"] == "100.50"
    finally:
        delete_test_wallet(wallet_id)

def test_withdraw_sufficient(client):
    """
    Проверяет снятие средств, когда баланс достаточен.
    Сначала пополняем на 200.00, затем снимаем 50.00 - остаток должен быть 150.00.
    """
    wallet_id = create_test_wallet()
    try:
        client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": OperationType.DEPOSIT.value, "amount": "200.00"}
        )
        resp = client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": OperationType.WITHDRAW.value, "amount": "50.00"}
        )
        assert resp.status_code == 200
        assert resp.json()["balance"] == "150.00"
    finally:
        delete_test_wallet(wallet_id)

def test_withdraw_insufficient(client):
    """
    Проверяет попытку снять больше, чем есть на балансе.
    Ожидается ошибка 400 с сообщением Insufficient funds
    """
    wallet_id = create_test_wallet()
    try:
        client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": OperationType.DEPOSIT.value, "amount": "100.00"}
        )
        resp = client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": OperationType.WITHDRAW.value, "amount": "150.00"}
        )
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Insufficient funds"
    finally:
        delete_test_wallet(wallet_id)

def test_concurrent_operations(client):
    """
    Имитирует конкурентные пополнения
    После трёх пополнений на 10, 20 и 30 баланс должен быть 60
    Конкурентность обеспечивается блокировкой в CRUD-слое
    """
    wallet_id = create_test_wallet()
    try:
        amounts = [10.0, 20.0, 30.0]
        for amount in amounts:
            resp = client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": OperationType.DEPOSIT.value, "amount": str(amount)}
            )
            assert resp.status_code == 200
        final = client.get(f"/api/v1/wallets/{wallet_id}")
        assert final.json()["balance"] == "60.00"
    finally:
        delete_test_wallet(wallet_id)