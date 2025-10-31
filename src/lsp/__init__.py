"""Punto de entrada de compatibilidad para el paquete ``lsp``.

Este módulo expone los componentes definidos en :mod:`pcobra.lsp` para
conservar importaciones heredadas como ``import lsp.server`` sin requerir
que el paquete completo esté instalado como dependencia separada.
"""

from __future__ import annotations

import importlib
import sys

__all__ = ["server", "cobra_plugin"]

_plugin_mod = sys.modules.get("lsp.cobra_plugin")
if _plugin_mod is None:
    try:
        _plugin_mod = importlib.import_module("pcobra.lsp.cobra_plugin")
        sys.modules["lsp.cobra_plugin"] = _plugin_mod
    except ModuleNotFoundError:  # pragma: no cover - dependencia opcional
        _plugin_mod = None

_server_mod = sys.modules.get("lsp.server")
if _server_mod is None:
    try:
        _server_mod = importlib.import_module("pcobra.lsp.server")
        sys.modules["lsp.server"] = _server_mod
    except ModuleNotFoundError:  # pragma: no cover - dependencia opcional
        _server_mod = None

if _plugin_mod is not None:
    cobra_plugin = _plugin_mod  # type: ignore

if _server_mod is not None:
    server = _server_mod  # type: ignore

