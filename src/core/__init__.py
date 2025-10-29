"""Compatibilidad para importaciones absolutas del antiguo paquete ``core``.

Este módulo delega todas las referencias a :mod:`pcobra.core` para que el
código legado que utilice ``import core`` continúe funcionando sin necesidad de
ajustes adicionales. Se replica la ruta de búsqueda del paquete original para
que ``import core.algo`` cargue los submódulos reales de ``pcobra.core``.
"""

from __future__ import annotations

from importlib import import_module
import sys
from types import ModuleType

_target_name = "pcobra.core"
_target: ModuleType = import_module(_target_name)

# Copiar el API público conocido para mantener compatibilidad inmediata.
__all__ = list(getattr(_target, "__all__", ()))
for _name in __all__:
    globals()[_name] = getattr(_target, _name)

# Mantener la ruta del paquete para que ``import core.algo`` localice los
# submódulos reales alojados en ``pcobra.core``.
__path__ = list(getattr(_target, "__path__", []))


def __getattr__(name: str):
    """Delegar dinámicamente los atributos al paquete ``pcobra.core``."""

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
    """Unificar el ``dir()`` del módulo con el del paquete objetivo."""

    atributos: set[str] = set(__all__) | set(globals()) | set(dir(_target))
    atributos.discard("_target")
    atributos.discard("_target_name")
    return sorted(atributos)


# Registrar alias explícitos para evitar duplicados cuando se importan ambos
# paquetes en diferentes órdenes.
sys.modules.setdefault(_target_name, _target)
sys.modules.setdefault(__name__, sys.modules[__name__])
for _mod_name, _mod in list(sys.modules.items()):
    if _mod_name.startswith(f"{_target_name}."):
        alias = __name__ + _mod_name[len(_target_name):]
        sys.modules.setdefault(alias, _mod)
