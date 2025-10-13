"""Paquete principal de Cobra."""

import importlib
import importlib.util
import logging
import sys as _sys

logger = logging.getLogger(__name__)

# Cargar primero los paquetes base para evitar errores de dependencias cruzadas
_submodules = ["cobra", "core", "cli", "ia", "jupyter_kernel", "gui", "lsp", "compiler"]

for pkg in _submodules:
    if importlib.util.find_spec(f".{pkg}", __name__) is None:
        logger.warning("Subm\u00f3dulo %s no encontrado, se omite su importaci\u00f3n", pkg)
        continue
    try:
        module = importlib.import_module(f".{pkg}", __name__)
        globals()[pkg] = module
        _sys.modules.setdefault(pkg, module)
    except ImportError as e:
        logger.warning("No se pudo importar %s: %s", pkg, e)
    except Exception as e:  # nosec B110
        logger.error("Error al importar %s", pkg, exc_info=True)
        raise

# Registrar alias de compatibilidad para importaciones absolutas heredadas
def _registrar_alias_legacy() -> None:
    """Sincroniza los nombres históricos ``cobra`` y ``core`` con ``pcobra``."""

    cobra_spec = importlib.util.find_spec("pcobra.cobra")
    if cobra_spec is None:
        return

    cobra_pkg = importlib.import_module("pcobra.cobra")
    _sys.modules.setdefault("cobra", cobra_pkg)

    core_spec = importlib.util.find_spec("pcobra.cobra.core")
    if core_spec is not None:
        core_pkg = importlib.import_module("pcobra.cobra.core")
        _sys.modules.setdefault("cobra.core", core_pkg)
        for nombre, modulo in list(_sys.modules.items()):
            if nombre.startswith("pcobra.cobra.core."):
                alias = "cobra.core." + nombre.split("pcobra.cobra.core.", 1)[1]
                _sys.modules.setdefault(alias, modulo)

    legacy_core_spec = importlib.util.find_spec("pcobra.core")
    if legacy_core_spec is None:
        return

    legacy_core = importlib.import_module("pcobra.core")
    _sys.modules.setdefault("core", legacy_core)
    for nombre, modulo in list(_sys.modules.items()):
        if nombre.startswith("pcobra.core."):
            alias = "core." + nombre.split("pcobra.core.", 1)[1]
            _sys.modules.setdefault(alias, modulo)


_registrar_alias_legacy()
