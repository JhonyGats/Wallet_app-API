import pytest
import subprocess
import time
import socket
import os
import signal
import sys
import httpx
from typing import Generator

@pytest.fixture(scope="session")
def app_server():
    """Запускает uvicorn сервер в отдельном процессе для тестирования"""
    # Определяем свободный порт
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()

    # Запускаем uvicorn как подпроцесс
    env = os.environ.copy()
    env["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@db:5432/wallet_db"
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(port)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Ждём, пока сервер запустится
    timeout = 10
    while timeout > 0:
        try:
            with httpx.Client() as client:
                resp = client.get(f"http://localhost:{port}/docs")
                if resp.status_code == 200:
                    break
        except:
            pass
        time.sleep(0.5)
        timeout -= 0.5
    else:
        proc.kill()
        raise RuntimeError("Server did not start")

    yield f"http://localhost:{port}"

    # Останавливаем сервер
    proc.send_signal(signal.SIGINT)
    proc.wait(timeout=5)

@pytest.fixture
def client(app_server):
    """HTTP клиент для тестирования"""
    with httpx.Client(base_url=app_server) as client:
        yield client