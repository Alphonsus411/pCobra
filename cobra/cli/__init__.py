"""Paquete puente que expone ``pcobra.cobra.cli`` como ``cobra.cli``."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
import sys
from types import ModuleType

_target_name = "pcobra.cobra.cli"
_target: ModuleType = import_module(_target_name)

__all__ = list(getattr(_target, "__all__", ()))
for _name in __all__:
    globals()[_name] = getattr(_target, _name)

_local_path = Path(__file__).resolve().parent
_target_paths = list(getattr(_target, "__path__", []))
__path__ = [str(_local_path), *map(str, _target_paths)]


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
sys.modules.pop(f"{__name__}.cli", None)
