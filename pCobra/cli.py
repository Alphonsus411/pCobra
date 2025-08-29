"""Accesos a la interfaz de línea de comandos.

Este módulo actúa como un puente hacia ``src.cli`` para poder
importar ``main`` desde ``pCobra.cli``.
"""

from src.cli import main

__all__ = ["main"]
