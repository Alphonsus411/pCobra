"""Bootstrapper para exponer ``pcobra`` durante el desarrollo.

Este módulo delega toda la funcionalidad al paquete real ubicado en
``src/pcobra``. Permite que ``python -m pcobra.cli`` funcione sin tener
que instalar previamente el proyecto.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

_SRC_PACKAGE = Path(__file__).resolve().parent.parent / "src" / "pcobra" / "__init__.py"

if not _SRC_PACKAGE.exists():  # pragma: no cover - entorno corrupto
    raise ModuleNotFoundError(
        "No se encontró el paquete pcobra dentro de src/. Verifique la estructura del repositorio."
    )

_spec = spec_from_file_location(
    __name__,
    _SRC_PACKAGE,
    submodule_search_locations=[str(_SRC_PACKAGE.parent)],
)
_module = module_from_spec(_spec)
_module.__package__ = __name__
_module.__file__ = str(_SRC_PACKAGE)
_module.__path__ = [str(_SRC_PACKAGE.parent)]  # type: ignore[attr-defined]

sys.modules[__name__] = _module
assert _spec.loader is not None  # ayuda a mypy
_spec.loader.exec_module(_module)
