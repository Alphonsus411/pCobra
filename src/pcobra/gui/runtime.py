"""Runtime compartido para las interfaces GUI de Cobra."""

from __future__ import annotations

import io
import re
from contextlib import redirect_stderr, redirect_stdout
from functools import lru_cache
from typing import Any


@lru_cache(maxsize=1)
def require_gui_dependencies() -> dict[str, Any]:
    """Importa dependencias de núcleo/transpiladores de forma diferida."""
    try:
        from pcobra.cobra.gui import deps as gui_deps
    except (ImportError, ModuleNotFoundError) as exc:  # pragma: no cover - validado desde CLI
        missing_target, action = _parse_missing_target(exc)
        detail = str(exc) or repr(exc)
        raise RuntimeError(
            "Error de importación GUI en 'pcobra.gui.runtime': "
            f"faltante detectado '{missing_target}'. "
            f"Detalle: {detail}. "
            f"Acción sugerida: {action}"
        ) from exc

    return {
        "Lexer": gui_deps.Lexer,
        "LexerError": gui_deps.LexerError,
        "Parser": gui_deps.Parser,
        "ParserError": gui_deps.ParserError,
        "target_cli_choices": gui_deps.target_cli_choices,
        "OFFICIAL_TARGETS": gui_deps.OFFICIAL_TARGETS,
        "InterpretadorCobra": gui_deps.InterpretadorCobra,
        "TRANSPILERS": gui_deps.get_transpilers(),
    }


def _parse_missing_target(exc: ImportError) -> tuple[str, str]:
    """Detecta el objetivo de importación faltante y sugiere acción."""
    detail = str(exc) or repr(exc)
    if isinstance(exc, ModuleNotFoundError):
        missing_module = getattr(exc, "name", None) or "desconocido"
        return missing_module, _dependency_action(missing_module)

    cannot_import_match = re.search(r"cannot import name '([^']+)' from '([^']+)'", detail)
    if cannot_import_match:
        symbol_name, module_name = cannot_import_match.groups()
        target = f"{module_name}.{symbol_name}"
        return target, _local_import_action(module_name, symbol_name)

    missing_module = getattr(exc, "name", None) or "desconocido"
    return missing_module, _dependency_action(missing_module)


def _dependency_action(missing_module: str) -> str:
    if missing_module.startswith("pcobra."):
        return (
            "corrige el import local y verifica que el módulo exista; "
            "si hace falta reinstala con 'pip install -e .'."
        )
    return f"instala la dependencia que provee '{missing_module}' o ajusta el import local."


def _local_import_action(module_name: str, symbol_name: str) -> str:
    return (
        f"corrige el import local de '{module_name}.{symbol_name}' "
        "o actualiza la dependencia que lo expone."
    )


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


def formatear_error(
    exc: Exception,
    *,
    lexer_error_type: type[BaseException] | None = None,
    parser_error_type: type[BaseException] | None = None,
) -> str:
    """Convierte excepciones en mensajes legibles para la GUI.

    ``lexer_error_type`` y ``parser_error_type`` se inyectan desde una capa ya
    inicializada (GUI handlers) para evitar imports/reloads en esta ruta de
    manejo de errores.
    """
    if lexer_error_type is not None and isinstance(exc, lexer_error_type):
        linea = getattr(exc, "linea", "?")
        columna = getattr(exc, "columna", "?")
        return f"Error léxico (línea {linea}, columna {columna}): {exc}"
    if parser_error_type is not None and isinstance(exc, parser_error_type):
        return f"Error de sintaxis: {exc}"
    return f"Error de ejecución: {exc}"


def gui_target_choices() -> tuple[str, ...]:
    """Devuelve targets canónicos visibles en GUI preservando el orden oficial."""
    deps = require_gui_dependencies()
    return deps["target_cli_choices"](
        set(deps["OFFICIAL_TARGETS"]) & set(deps["TRANSPILERS"])
    )
