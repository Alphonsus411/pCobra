"""Herramientas asincrónicas expuestas en la biblioteca estándar."""

from __future__ import annotations

from typing import Any, AsyncContextManager

from pcobra.corelibs import grupo_tareas as _grupo_tareas

__all__ = ["grupo_tareas"]


def grupo_tareas() -> AsyncContextManager[Any]:
    """Crea un grupo de tareas que replica la semántica de ``asyncio.TaskGroup``.

    Este envoltorio delega en :func:`pcobra.corelibs.grupo_tareas` para ofrecer un
    administrador que espera a que todas las tareas finalicen y cancela las
    pendientes cuando se produce un error. Resulta útil para escribir código Cobra
    que requiera coordinar corrutinas en Python 3.10 o versiones anteriores donde
    ``asyncio.TaskGroup`` todavía no existe.
    """

    return _grupo_tareas()
