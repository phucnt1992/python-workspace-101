import importlib.util
import sys
from pathlib import Path

_cli_src = Path(__file__).parent / "src"

# Ensure the cli package is registered with the correct source path so its
# submodules (cli.main, cli.exp, …) are discoverable during pytest collection.
_pkg_spec = importlib.util.spec_from_file_location(
    "cli",
    _cli_src / "cli" / "__init__.py",
    submodule_search_locations=[str(_cli_src / "cli")],
)
assert _pkg_spec and _pkg_spec.loader
if "cli" not in sys.modules:
    _pkg_mod = importlib.util.module_from_spec(_pkg_spec)
    sys.modules["cli"] = _pkg_mod
    _pkg_spec.loader.exec_module(_pkg_mod)  # type: ignore[union-attr]
else:
    # Patch the search path so submodule imports resolve to the source tree
    sys.modules["cli"].__path__ = [str(_cli_src / "cli")]  # type: ignore[attr-defined]

_actual = _cli_src / "cli" / "main.py"
_spec = importlib.util.spec_from_file_location("cli.main", _actual)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("cli.main", _mod)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

app = _mod.app

if __name__ == "__main__":
    app()
