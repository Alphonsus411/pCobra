"""Paquete principal de Cobra."""

import importlib
import importlib.util
import logging

logger = logging.getLogger(__name__)

_submodules = ["cli", "cobra", "core", "ia", "jupyter_kernel", "gui", "lsp"]

for pkg in _submodules:
    if importlib.util.find_spec(f".{pkg}", __name__) is None:
        logger.warning("Subm\u00f3dulo %s no encontrado, se omite su importaci\u00f3n", pkg)
        continue
    try:
        module = importlib.import_module(f".{pkg}", __name__)
        globals()[pkg] = module
    except Exception as e:  # nosec B110
        logger.warning("No se pudo importar %s: %s", pkg, e)
