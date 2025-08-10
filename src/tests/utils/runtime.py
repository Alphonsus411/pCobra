"""Utilidades para ejecutar código en distintos lenguajes durante los tests."""
from __future__ import annotations

from typing import Callable, Dict

from core.sandbox import ejecutar_en_sandbox, ejecutar_en_sandbox_js


def _run_python(code: str) -> str:
    """Ejecuta código Python en la sandbox interna y devuelve la salida."""
    return ejecutar_en_sandbox(code)


def _run_js(code: str) -> str:
    """Ejecuta código JavaScript usando Node.js y devuelve la salida."""
    return ejecutar_en_sandbox_js(code)


_RUNNERS: Dict[str, Callable[[str], str]] = {
    "python": _run_python,
    "js": _run_js,
}


def run_code(lang: str, code: str) -> str:
    """Ejecuta *code* en el lenguaje indicado y devuelve la salida estándar.

    Parameters
    ----------
    lang: str
        Identificador del lenguaje (por ejemplo ``"python"`` o ``"js"``).
    code: str
        Código fuente a ejecutar.

    Returns
    -------
    str
        Salida producida por el programa.

    Raises
    ------
    ValueError
        Si el lenguaje no está soportado.
    """
    try:
        runner = _RUNNERS[lang]
    except KeyError as exc:  # pragma: no cover - caso simple
        raise ValueError(f"Lenguaje no soportado: {lang}") from exc
    return runner(code)
