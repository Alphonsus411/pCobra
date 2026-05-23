from __future__ import annotations

import shutil
import subprocess

from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_error


def format_code_with_black(archivo: str) -> bool:
    """Formatea un archivo de código usando black."""
    try:
        if not shutil.which("black"):
            mostrar_error(_("Herramienta 'black' no encontrada en el PATH"), registrar_log=False)
            return False

        resultado = subprocess.run(
            ["black", archivo],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if resultado.returncode != 0:
            mostrar_error(f"Error al formatear: {resultado.stderr}", registrar_log=False)
            return False
        return True
    except Exception as exc:  # pragma: no cover - salvaguarda defensiva CLI
        mostrar_error(f"Error inesperado al formatear: {exc}", registrar_log=False)
        return False
