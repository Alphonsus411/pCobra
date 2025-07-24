import importlib
import logging
import sys

logging.basicConfig(level=logging.INFO)

for pkg in ["cli", "cobra", "core", "ia", "jupyter_kernel", "tests"]:
    try:
        module = importlib.import_module(pkg)
        sys.modules[__name__ + "." + pkg] = module
    except Exception as e:  # nosec B110
        logging.warning("No se pudo importar %s: %s", pkg, e)
