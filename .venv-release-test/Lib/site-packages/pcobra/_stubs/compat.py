"""Cargadores de dependencias opcionales con fallback seguro a stubs internos."""

from __future__ import annotations

import importlib
from typing import Any

_SAFE_STUB_MODULES = {
    "numpy": "pcobra._stubs.numpy",
    "pandas": "pcobra._stubs.pandas",
    "pexpect": "pcobra._stubs.pexpect",
    "rich": "pcobra._stubs.rich",
}


def _is_missing_target(error: ModuleNotFoundError, module_name: str) -> bool:
    missing = getattr(error, "name", None)
    if missing is None:
        return False
    return missing == module_name or missing.startswith(f"{module_name}.")


def import_optional_module(module_name: str, *, safe_stub: bool = False) -> Any:
    """Importa ``module_name`` y permite fallback explícito a stub interno seguro."""

    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if not _is_missing_target(exc, module_name):
            raise
        if not safe_stub:
            raise
        root_name = module_name.split(".", 1)[0]
        stub_root = _SAFE_STUB_MODULES.get(root_name)
        if stub_root is None:
            raise
        suffix = module_name[len(root_name) :]
        return importlib.import_module(f"{stub_root}{suffix}")


def import_optional_attr(module_name: str, attr_name: str, *, safe_stub: bool = False) -> Any:
    """Importa un atributo desde una dependencia opcional con fallback controlado."""

    module = import_optional_module(module_name, safe_stub=safe_stub)
    return getattr(module, attr_name)
