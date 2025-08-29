"""Habilita la resolución del paquete ``pCobra`` durante el desarrollo.

Python carga este módulo automáticamente al iniciar si se encuentra en
``sys.path``. Se añade la carpeta ``pCobra`` del repositorio para
permitir los imports ``from pCobra.modulo import ...`` sin haber
instalado el paquete previamente.
"""

from pathlib import Path
import sys

PCOBRA_PATH = Path(__file__).resolve().parent / "pCobra"
if PCOBRA_PATH.exists():
    sys.path.insert(0, str(PCOBRA_PATH))
