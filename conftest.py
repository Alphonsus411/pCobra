"""Configuración de Pytest específica para ejecutar pruebas asíncronas."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
import sys

SRC_PATH = Path(__file__).resolve().parent / 'src'
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

try:  # pragma: no cover - protege entornos sin alias instalados
    import importlib

    sys.modules.setdefault('core', importlib.import_module('core'))
    sys.modules.setdefault('cobra', importlib.import_module('cobra'))
except ModuleNotFoundError:
    pass

import asyncio
import inspect
from typing import Any


def _restore_alias(module_name: str, alias: str) -> None:
    """Garantiza que el alias ``alias`` apunte al módulo real."""

    module = import_module(module_name)
    sys.modules[alias] = module
    prefix = f"{module_name}."
    alias_prefix = f"{alias}."
    for name, mod in list(sys.modules.items()):
        if name.startswith(prefix):
            sys.modules[alias_prefix + name[len(prefix) :]] = mod


def pytest_runtest_setup(item):  # noqa: ARG001
    """Restaura los alias dinámicos antes de cada prueba."""

    for prefix in ("cobra.transpilers", "pcobra.cobra.transpilers"):
        for name in [mod for mod in sys.modules if mod.startswith(prefix)]:
            sys.modules.pop(name, None)
    _restore_alias("pcobra.core", "core")
    _restore_alias("pcobra.cobra", "cobra")


def pytest_collectstart(collector):  # noqa: ARG001
    _restore_alias("pcobra.core", "core")
    _restore_alias("pcobra.cobra", "cobra")


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
