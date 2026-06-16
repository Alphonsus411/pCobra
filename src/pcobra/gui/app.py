"""Compatibilidad para la entrada GUI pública de Cobra.

La implementación canónica de la interfaz gráfica vive en
``pcobra.gui.idle.main``. Este módulo conserva ``pcobra.gui.app.main`` como
alias público para integraciones históricas, evitando duplicar layout, botones
y handlers.
"""

from pcobra.gui import runtime
from pcobra.gui.idle import main

__all__ = ["main", "runtime"]


if __name__ == "__main__":
    runtime.flet_app(main)
