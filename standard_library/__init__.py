"""Compatibilidad para ``pcobra.standard_library``."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
import sys
from types import ModuleType

_target_name = "pcobra.standard_library"
_target: ModuleType = import_module(_target_name)

__all__ = [name for name in getattr(_target, "__all__", ()) if hasattr(_target, name)]
for _name in __all__:
    globals()[_name] = getattr(_target, _name)

_local_path = Path(__file__).resolve().parent
__path__ = [str(_local_path), *map(str, getattr(_target, "__path__", []))]


def __getattr__(name: str):
    try:
        value = getattr(_target, name)
    except AttributeError as exc:  # pragma: no cover - delegación directa
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    atributos = set(__all__) | set(globals()) | set(dir(_target))
    atributos.discard("_target")
    atributos.discard("_target_name")
    return sorted(atributos)


sys.modules.setdefault(_target_name, _target)
