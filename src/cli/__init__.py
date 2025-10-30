"""Alias compatible para el paquete ``pcobra.cobra``.

Permite que ``import cli`` y ``python -m cli.cli`` sigan funcionando en
entornos que esperaban el paquete histórico ``cli``. Se reexporta el paquete
original para mantener la compatibilidad con los submódulos.
"""

from __future__ import annotations

from importlib import import_module
import sys
from pathlib import Path
from types import ModuleType
from typing import Iterable

_target = import_module("pcobra.cobra")

# Registra alias en ``sys.modules`` para mantener referencias únicas.
sys.modules.setdefault("pcobra.cobra", _target)
sys.modules.setdefault(__name__, _target)

__all__ = getattr(_target, "__all__", [])

_target_paths: Iterable[str] = getattr(_target, "__path__", [])
_local_path = str(Path(__file__).resolve().parent)
__path__ = [_local_path, *[p for p in _target_paths if p != _local_path]]  # type: ignore[assignment]

for _name in __all__:
    globals()[_name] = getattr(_target, _name)

if not isinstance(_target, ModuleType):  # pragma: no cover - caso defensivo
    raise RuntimeError("pcobra.cobra no es un módulo válido")
