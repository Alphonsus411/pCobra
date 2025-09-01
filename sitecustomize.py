"""Habilita la resolución del paquete ``pcobra`` durante el desarrollo.

Python carga este módulo automáticamente al iniciar si se encuentra en
``sys.path``. Se añade la carpeta ``src/pcobra`` del repositorio para
permitir los imports ``from pcobra.modulo import ...`` sin haber
instalado el paquete previamente.
"""

from pathlib import Path
import sys

PCOBRA_PATH = Path(__file__).resolve().parent / "src" / "pcobra"
if PCOBRA_PATH.exists():
    sys.path.insert(0, str(PCOBRA_PATH))
