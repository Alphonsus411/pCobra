"""Políticas canónicas para la instrucción `usar`."""

from __future__ import annotations

from pcobra.cobra.usar_loader import USAR_COBRA_PUBLIC_MODULES

REPL_COBRA_MODULE_MAP: dict[str, str] = {
    modulo: modulo for modulo in USAR_COBRA_PUBLIC_MODULES
}
