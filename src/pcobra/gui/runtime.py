"""Runtime compartido para las interfaces GUI de Cobra."""

from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout
from functools import lru_cache
from typing import Any


@lru_cache(maxsize=1)
def require_gui_dependencies() -> dict[str, Any]:
    """Importa dependencias de núcleo/transpiladores de forma diferida."""
    try:
        from pcobra.cobra.cli.commands.compile_cmd import TRANSPILERS
        from pcobra.cobra.core import Lexer, LexerError, Parser, ParserError
        from pcobra.cobra.transpilers.target_utils import target_cli_choices
        from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
        from pcobra.core.interpreter import InterpretadorCobra
    except ModuleNotFoundError as exc:  # pragma: no cover - validado desde CLI
        raise RuntimeError(
            "Falta una dependencia de core/transpiladores para la GUI: "
            f"'{exc.name}'."
        ) from exc

    return {
        "Lexer": Lexer,
        "LexerError": LexerError,
        "Parser": Parser,
        "ParserError": ParserError,
        "target_cli_choices": target_cli_choices,
        "OFFICIAL_TARGETS": OFFICIAL_TARGETS,
        "InterpretadorCobra": InterpretadorCobra,
        "TRANSPILERS": TRANSPILERS,
    }


def require_flet() -> Any:
    """Importa Flet de forma diferida para no romper imports de CLI."""
    try:
        import flet as ft
    except ModuleNotFoundError as exc:  # pragma: no cover - validado desde CLI
        raise RuntimeError("Falta la dependencia 'flet'. Ejecuta: pip install flet.") from exc
    return ft


def normalizar_codigo(codigo: str | None) -> str:
    """Normaliza la entrada para evitar valores ``None``."""
    return codigo or ""


def ejecutar_codigo(codigo: str) -> str:
    """Ejecuta código Cobra y captura la salida impresa."""
    deps = require_gui_dependencies()
    buffer = io.StringIO()
    with redirect_stdout(buffer), redirect_stderr(buffer):
        tokens = deps["Lexer"](codigo).tokenizar()
        ast = deps["Parser"](tokens).parsear()
        deps["InterpretadorCobra"]().ejecutar_ast(ast)
    return buffer.getvalue()


def transpilar_codigo(codigo: str, lang: str) -> str:
    """Transpila código Cobra al lenguaje especificado."""
    deps = require_gui_dependencies()
    tokens = deps["Lexer"](codigo).tokenizar()
    ast = deps["Parser"](tokens).parsear()
    transp = deps["TRANSPILERS"][lang]()
    return transp.generate_code(ast)


def mostrar_tokens(codigo: str) -> str:
    """Tokeniza código Cobra y devuelve una representación por línea."""
    deps = require_gui_dependencies()
    tokens = deps["Lexer"](codigo).tokenizar()
    return "\n".join(str(token) for token in tokens)


def mostrar_ast(codigo: str) -> str:
    """Parsea código Cobra y devuelve una representación serializada del AST."""
    deps = require_gui_dependencies()
    tokens = deps["Lexer"](codigo).tokenizar()
    ast = deps["Parser"](tokens).parsear()
    return str(ast)


def formatear_error(exc: Exception) -> str:
    """Convierte excepciones en mensajes legibles para la GUI."""
    deps = require_gui_dependencies()
    if isinstance(exc, deps["LexerError"]):
        return f"Error léxico (línea {exc.linea}, columna {exc.columna}): {exc}"
    if isinstance(exc, deps["ParserError"]):
        return f"Error de sintaxis: {exc}"
    return f"Error de ejecución: {exc}"


def gui_target_choices() -> tuple[str, ...]:
    """Devuelve targets canónicos visibles en GUI preservando el orden oficial."""
    deps = require_gui_dependencies()
    return deps["target_cli_choices"](
        set(deps["OFFICIAL_TARGETS"]) & set(deps["TRANSPILERS"])
    )
