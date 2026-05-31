import importlib.util
from pathlib import Path

# Load the actual CLI implementation located under src/cli/src/cli/main.py
CLI_REAL_PATH = Path(__file__).resolve().parent / "src" / "cli" / "main.py"
spec = importlib.util.spec_from_file_location("todo_cli_main", CLI_REAL_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load CLI module from {CLI_REAL_PATH}")

cli_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli_main)

# Expose `app` for tests and external runners
app = getattr(cli_main, "app")

__all__ = ["app"]
