"""Compatibilidad para el paquete histórico ``cobra``.

El proyecto original exponía módulos como ``cobra.core`` y ``core`` en la raíz
del intérprete. Para facilitar la transición hacia ``pcobra`` mantenemos este
módulo delgado que delega en los paquetes reales y registra alias en
``sys.modules``. Así, los imports absolutos existentes continúan funcionando
sin modificaciones.
"""

from __future__ import annotations

from importlib import import_module
import sys
from types import ModuleType

_target_name = "pcobra.cobra"
_target: ModuleType = import_module(_target_name)

__all__ = list(getattr(_target, "__all__", ()))
for _name in __all__:
    globals()[_name] = getattr(_target, _name)


def __getattr__(name: str):
    """Delegar atributos en :mod:`pcobra.cobra` de forma perezosa."""

    try:
        valor = getattr(_target, name)
    except AttributeError as exc:  # pragma: no cover - delegación directa
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    else:
        globals()[name] = valor
        if isinstance(valor, ModuleType):
            sys.modules.setdefault(f"{__name__}.{name}", valor)
        return valor


def __dir__() -> list[str]:
    return sorted(set(__all__) | set(globals()) | set(dir(_target)))


# Asegurar que los alias clásicos siguen resolviéndose correctamente.
sys.modules.setdefault(_target_name, _target)
sys.modules.setdefault(f"{__name__}.core", import_module("pcobra.cobra.core"))
sys.modules.setdefault("core", import_module("pcobra.core"))
for _mod_name, _mod in list(sys.modules.items()):
    if _mod_name.startswith(f"{_target_name}."):
        alias = __name__ + _mod_name[len(_target_name):]
        sys.modules.setdefault(alias, _mod)
