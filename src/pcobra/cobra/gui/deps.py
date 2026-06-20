"""Dependencias neutrales de runtime para GUI.

Este módulo evita acoplar GUI con rutas de comandos CLI concretas.
Expone únicamente:
- Lexer/Parser (+ tipos de error asociados)
- intérprete
- registro de transpiladores
- helpers/choices de targets
"""

from __future__ import annotations

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.core import Lexer, LexerError, Parser, ParserError
from pcobra.cobra.transpilers.registry import get_transpilers
from pcobra.cobra.transpilers.target_utils import target_cli_choices
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from pcobra.cobra.core.interpreter import InterpretadorCobra

if tuple(OFFICIAL_TARGETS) != PUBLIC_BACKENDS:
    raise RuntimeError(
        "Contrato público inválido en GUI deps: OFFICIAL_TARGETS debe coincidir "
        f"exactamente con PUBLIC_BACKENDS. official={tuple(OFFICIAL_TARGETS)}; "
        f"public={PUBLIC_BACKENDS}"
    )

__all__ = [
    "Lexer",
    "LexerError",
    "Parser",
    "ParserError",
    "InterpretadorCobra",
    "get_transpilers",
    "target_cli_choices",
    "OFFICIAL_TARGETS",
]
