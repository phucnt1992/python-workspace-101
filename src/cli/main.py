from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR / "src"))
_APP_MAIN_PATH = _THIS_DIR / "src" / "cli" / "main.py"

_spec = spec_from_file_location("cli_runtime_main", _APP_MAIN_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Cannot load CLI app module from {_APP_MAIN_PATH}")

_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)
app = _module.app


if __name__ == "__main__":
    app()
