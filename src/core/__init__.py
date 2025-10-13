"""Compatibilidad para importaciones absolutas del antiguo paquete ``core``.

Este módulo delega todas las referencias a :mod:`pcobra.core` para que el
código legado que utilice ``import core`` continúe funcionando sin necesidad de
ajustes adicionales. Se replica la ruta de búsqueda del paquete original para
que ``import core.algo`` cargue los submódulos reales de ``pcobra.core``.
"""

from importlib import import_module
import sys
from types import ModuleType

_target_name = "pcobra.core"
_target: ModuleType = import_module(_target_name)

# Exponer el mismo API público que el paquete objetivo.
__all__ = getattr(_target, "__all__", [])
for _name in __all__:
    globals()[_name] = getattr(_target, _name)

# Mantener la ruta del paquete para permitir la carga de submódulos reales.
__path__ = list(getattr(_target, "__path__", []))


def __getattr__(name: str):
    """Delegar atributos al paquete ``pcobra.core``."""
    return getattr(_target, name)


def __dir__() -> list[str]:
    """Unificar el ``dir()`` del módulo con el de ``pcobra.core``."""
    return sorted(set(__all__) | set(dir(_target)))


# Registrar explícitamente el alias para que ``sys.modules['core']`` y
# ``sys.modules['pcobra.core']`` apunten al mismo objeto y evitar duplicados.
sys.modules[__name__] = _target
