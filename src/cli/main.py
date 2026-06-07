"""Compatibility entrypoint for tests that import src/cli/main.py directly."""

import importlib.util
from pathlib import Path

_CLI_MAIN_PATH = Path(__file__).resolve().parent / "src" / "cli" / "main.py"
_spec = importlib.util.spec_from_file_location("todo_cli_main", _CLI_MAIN_PATH)
if _spec is None or _spec.loader is None:
	raise RuntimeError(f"Cannot load CLI module from {_CLI_MAIN_PATH}")

_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

app = _module.app
