"""Configuración de Pytest específica para ejecutar pruebas asíncronas."""

from __future__ import annotations

from pathlib import Path
import sys

SRC_PATH = Path(__file__).resolve().parent / 'src'
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import asyncio
import inspect
from typing import Any


def pytest_runtest_setup(item):  # noqa: ARG001
    """Aísla los módulos de transpiladores cargados por cada prueba."""

    for prefix in ("cobra.transpilers", "pcobra.cobra.transpilers"):
        for name in [mod for mod in sys.modules if mod.startswith(prefix)]:
            sys.modules.pop(name, None)


def _ejecutar_corutina(funcion, **kwargs: Any) -> None:
    bucle = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(bucle)
        bucle.run_until_complete(funcion(**kwargs))
    finally:
        bucle.run_until_complete(bucle.shutdown_asyncgens())
        asyncio.set_event_loop(None)
        bucle.close()


def pytest_pyfunc_call(pyfuncitem):  # type: ignore[override]
    """Permite ejecutar funciones marcadas con ``@pytest.mark.asyncio``."""

    funcion = pyfuncitem.obj  # type: ignore[attr-defined]
    if inspect.iscoroutinefunction(funcion):
        marker = pyfuncitem.get_closest_marker("asyncio")
        if marker is not None:
            argumentos = {
                nombre: pyfuncitem.funcargs[nombre]
                for nombre in pyfuncitem._fixtureinfo.argnames  # type: ignore[attr-defined]
            }
            _ejecutar_corutina(funcion, **argumentos)
            return True
    return None
