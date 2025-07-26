"""Paquete principal de Cobra."""

import importlib
import logging

logger = logging.getLogger(__name__)

_submodules = ["cli", "cobra", "core", "ia", "jupyter_kernel", "gui", "lsp"]

for pkg in _submodules:
    try:
        module = importlib.import_module(f".{pkg}", __name__)
        globals()[pkg] = module
    except Exception as e:  # nosec B110
        logger.warning("No se pudo importar %s: %s", pkg, e)
