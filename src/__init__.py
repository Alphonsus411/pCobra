"""Paquete principal de Cobra."""

import importlib
import logging

logging.basicConfig(level=logging.INFO)

for pkg in ["cli", "cobra", "core", "ia", "jupyter_kernel", "tests", "gui", "lsp"]:
    try:
        module = importlib.import_module(f".{pkg}", __name__)
        globals()[pkg] = module
    except Exception as e:  # nosec B110
        logging.warning("No se pudo importar %s: %s", pkg, e)
