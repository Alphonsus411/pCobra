"""Compatibilidad para el paquete histórico ``cobra``.

El proyecto original exponía módulos como ``cobra.core`` y ``core`` en la raíz
del intérprete. Para facilitar la transición hacia ``pcobra`` mantenemos este
módulo delgado que delega en los paquetes reales y registra alias en
``sys.modules``. Así, los imports absolutos existentes continúan funcionando
sin modificaciones.
"""

from importlib import import_module
import sys
from types import ModuleType

_target_name = "pcobra.cobra"
_target: ModuleType = import_module(_target_name)

# Permitir que ``import cobra`` entregue el paquete real.
sys.modules[__name__] = _target

# Asegurar que ``cobra.core`` resuelva al núcleo actualizado.
sys.modules.setdefault(f"{__name__}.core", import_module("pcobra.cobra.core"))

# Mantener ``import core`` para código heredado cuando solo se invoca ``import cobra``.
sys.modules.setdefault("core", import_module("pcobra.core"))
