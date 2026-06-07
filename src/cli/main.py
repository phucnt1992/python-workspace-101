"""CLI entry point.

Loads the Typer ``app`` from the real ``cli.main`` module by file path so it
works whether imported as the installed package or executed standalone. The
acceptance tests load this file directly, and ``tests/cli`` is itself a package
named ``cli`` that would otherwise shadow the real package on ``sys.path``.
"""

import importlib.util
from pathlib import Path

_main_path = Path(__file__).parent / "src" / "cli" / "main.py"
_spec = importlib.util.spec_from_file_location("cli_main_impl", _main_path)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Cannot load CLI module from {_main_path}")

_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

app = _module.app

if __name__ == "__main__":
    app()
