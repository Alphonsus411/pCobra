"""Configuración de Pytest específica para ejecutar pruebas asíncronas."""

from __future__ import annotations

from importlib import import_module
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from pathlib import Path
import sys

SRC_PATH = Path(__file__).resolve().parent / 'src'
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import asyncio
import inspect
from types import ModuleType
from typing import Any


class _CanonicalAliasLoader(Loader):
    """Carga un nombre histórico reutilizando el módulo canónico."""

    def __init__(self, canonical_name: str) -> None:
        self.canonical_name = canonical_name
        self._metadata: tuple[object, object, object] | None = None

    def create_module(self, spec: ModuleSpec) -> ModuleType:  # noqa: ARG002
        module = import_module(self.canonical_name)
        self._metadata = (module.__spec__, module.__loader__, module.__package__)
        return module

    def exec_module(self, module: ModuleType) -> None:
        # El mecanismo de importación escribe los metadatos del alias sobre el
        # objeto retornado por ``create_module``; se conserva su identidad
        # canónica para introspección e importaciones relativas posteriores.
        if self._metadata is not None:
            module.__spec__, module.__loader__, module.__package__ = self._metadata


class _CanonicalAliasFinder(MetaPathFinder):
    """Redirige submódulos legacy antes de que ``PathFinder`` los duplique."""

    _prefixes = {"cobra.": "pcobra.cobra.", "core.": "pcobra.core."}

    def find_spec(
        self,
        fullname: str,
        path: object = None,  # noqa: ARG002
        target: ModuleType | None = None,  # noqa: ARG002
    ) -> ModuleSpec | None:
        for legacy_prefix, canonical_prefix in self._prefixes.items():
            if fullname.startswith(legacy_prefix):
                canonical_name = canonical_prefix + fullname[len(legacy_prefix) :]
                return ModuleSpec(
                    fullname,
                    _CanonicalAliasLoader(canonical_name),
                    is_package=False,
                )
        return None


_ALIAS_FINDER = _CanonicalAliasFinder()
if not any(isinstance(finder, _CanonicalAliasFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, _ALIAS_FINDER)


def _restore_cobra_alias() -> None:
    """Mantiene ``cobra`` enlazado al paquete canónico durante las pruebas."""

    module_name = "pcobra.cobra"
    alias = "cobra"
    module = import_module(module_name)
    sys.modules[alias] = module
    prefix = f"{module_name}."
    alias_prefix = f"{alias}."
    for name, loaded_module in list(sys.modules.items()):
        if name.startswith(prefix):
            sys.modules[alias_prefix + name[len(prefix) :]] = loaded_module


def _prepare_core_submodule_aliases() -> None:
    """Evita duplicar submódulos de ``pcobra.core`` sin cargar el shim ``core``."""

    module_name = "pcobra.core"
    alias = "core"
    import_module(module_name)
    sys.modules.pop(alias, None)
    prefix = f"{module_name}."
    alias_prefix = f"{alias}."
    for name, loaded_module in list(sys.modules.items()):
        if name.startswith(prefix):
            sys.modules[alias_prefix + name[len(prefix) :]] = loaded_module


# Se registra antes de que ``tests/conftest.py`` añada ``src/pcobra`` al path;
# así nunca se crea un segundo árbol de módulos bajo el nombre histórico.
_restore_cobra_alias()
_prepare_core_submodule_aliases()


def pytest_runtest_setup(item):  # noqa: ARG001
    """Aísla los módulos de transpiladores cargados por cada prueba."""

    for prefix in ("cobra.transpilers", "pcobra.cobra.transpilers"):
        for name in [mod for mod in sys.modules if mod.startswith(prefix)]:
            sys.modules.pop(name, None)
    _restore_cobra_alias()


def pytest_collectstart(collector):  # noqa: ARG001
    """Restaura el alias canónico antes de importar cada módulo de pruebas."""

    _restore_cobra_alias()


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
