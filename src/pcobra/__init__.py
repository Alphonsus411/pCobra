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
