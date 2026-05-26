import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_server_ready(base_url: str, timeout_seconds: int = 30) -> None:
    started = time.monotonic()
    health_url = f"{base_url}/api/_healthz/liveness"
    while (time.monotonic() - started) < timeout_seconds:
        try:
            with urlopen(health_url, timeout=1.0) as response:  # noqa: S310
                if response.status == 200:
                    return
        except URLError:
            pass
        time.sleep(0.2)
    raise TimeoutError(f"Timed out waiting for server at {health_url}")


@pytest.fixture(scope="session")
def app_url(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    temp_dir = tmp_path_factory.mktemp("e2e-server")
    db_file = temp_dir / "todos-e2e.db"
    port = _find_free_port()
    base_url = f"http://127.0.0.1:{port}"

    env = os.environ.copy()
    env["APP_DB_URL"] = f"sqlite+aiosqlite:///{db_file}"

    server_process = subprocess.Popen(  # noqa: S603
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=ROOT_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        _wait_for_server_ready(base_url)
        yield base_url
    finally:
        server_process.terminate()
        try:
            server_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait(timeout=5)
