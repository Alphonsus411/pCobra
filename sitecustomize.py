"""Habilita la resolución del paquete ``pcobra`` durante el desarrollo.

Python carga este módulo automáticamente al iniciar si se encuentra en
``sys.path``. Se añade la carpeta ``src`` del repositorio para permitir
los imports ``from pcobra.modulo import ...`` sin haber instalado el
paquete previamente.
"""

from pathlib import Path
import sys

SRC_PATH = Path(__file__).resolve().parent / "src"
if SRC_PATH.exists():
    sys.path.insert(0, str(SRC_PATH))

    # Asegurar que el alias ``core`` apunte al paquete real incluso si existen
    # carpetas de pruebas con el mismo nombre en el ``sys.path``.
    try:  # pragma: no cover - depende del entorno de ejecución
        import importlib

        core_module = importlib.import_module("pcobra.core")
        sys.modules["core"] = core_module
    except ModuleNotFoundError:
        pass
