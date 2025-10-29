"""Alias de compatibilidad para ``pcobra.cobra``."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
import sys
from types import ModuleType

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

_target_name = "pcobra.cobra"
_target: ModuleType = import_module(_target_name)

__all__ = list(getattr(_target, "__all__", ()))
for _name in __all__:
    globals()[_name] = getattr(_target, _name)

__path__ = list(getattr(_target, "__path__", []))


def __getattr__(name: str):
    try:
        valor = getattr(_target, name)
    except AttributeError as exc:  # pragma: no cover - delegación directa
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    globals()[name] = valor
    if isinstance(valor, ModuleType):
        sys.modules.setdefault(f"{__name__}.{name}", valor)
    return valor


def __dir__() -> list[str]:
    atributos = set(__all__) | set(globals()) | set(dir(_target))
    atributos.discard("_target")
    atributos.discard("_target_name")
    return sorted(atributos)


sys.modules.setdefault(_target_name, _target)
sys.modules.setdefault(__name__, sys.modules[__name__])
for _mod_name, _mod in list(sys.modules.items()):
    if _mod_name.startswith(f"{_target_name}."):
        alias = __name__ + _mod_name[len(_target_name):]
        sys.modules.setdefault(alias, _mod)

sys.modules.setdefault("core", import_module("pcobra.core"))
