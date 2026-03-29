"""Entorno interactivo para ejecutar código Cobra y explorar tokens y AST."""

import io
from contextlib import redirect_stderr, redirect_stdout
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import flet as ft


def _require_gui_dependencies() -> dict[str, Any]:
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


def _ejecutar_codigo(codigo: str) -> str:
    """Ejecuta código Cobra y captura la salida impresa."""
    deps = _require_gui_dependencies()
    buffer = io.StringIO()
    with redirect_stdout(buffer), redirect_stderr(buffer):
        tokens = deps["Lexer"](codigo).tokenizar()
        ast = deps["Parser"](tokens).parsear()
        deps["InterpretadorCobra"]().ejecutar_ast(ast)
    return buffer.getvalue()


def _mostrar_tokens(codigo: str) -> str:
    deps = _require_gui_dependencies()
    tokens = deps["Lexer"](codigo).tokenizar()
    return "\n".join(str(t) for t in tokens)


def _mostrar_ast(codigo: str) -> str:
    deps = _require_gui_dependencies()
    tokens = deps["Lexer"](codigo).tokenizar()
    ast = deps["Parser"](tokens).parsear()
    return str(ast)


def _transpilar_codigo(codigo: str, lang: str) -> str:
    """Transpila código Cobra al lenguaje especificado."""
    deps = _require_gui_dependencies()
    tokens = deps["Lexer"](codigo).tokenizar()
    ast = deps["Parser"](tokens).parsear()
    transp = deps["TRANSPILERS"][lang]()
    return transp.generate_code(ast)


def _normalizar_codigo(codigo: str | None) -> str:
    """Normaliza la entrada para evitar valores ``None``."""
    return codigo or ""


def _formatear_error(exc: Exception) -> str:
    """Convierte excepciones en mensajes legibles para la GUI."""
    deps = _require_gui_dependencies()
    if isinstance(exc, deps["LexerError"]):
        return f"Error léxico (línea {exc.linea}, columna {exc.columna}): {exc}"
    if isinstance(exc, deps["ParserError"]):
        return f"Error de sintaxis: {exc}"
    return f"Error de ejecución: {exc}"


def _gui_target_choices() -> tuple[str, ...]:
    """Devuelve targets canónicos visibles en GUI preservando el orden oficial."""
    deps = _require_gui_dependencies()
    return deps["target_cli_choices"](
        set(deps["OFFICIAL_TARGETS"]) & set(deps["TRANSPILERS"])
    )


def _require_flet() -> Any:
    """Importa Flet de forma diferida para no romper imports de CLI."""
    try:
        import flet as ft
    except ModuleNotFoundError as exc:  # pragma: no cover - validado desde CLI
        raise RuntimeError("Falta la dependencia 'flet'. Ejecuta: pip install flet.") from exc
    return ft


def main(page: "ft.Page"):
    """Función principal para el entorno IDLE."""
    ft = _require_flet()

    entrada = ft.TextField(multiline=True, expand=True)
    salida = ft.Text(value="", selectable=True)
    lenguajes = list(_gui_target_choices())
    selector = ft.Dropdown(options=[ft.dropdown.Option(lang) for lang in lenguajes])
    activar = ft.Switch(label="Transpilar")

    def ejecutar_handler(e):
        deps = _require_gui_dependencies()
        codigo = _normalizar_codigo(entrada.value)
        try:
            if activar.value and selector.value in deps["TRANSPILERS"]:
                salida.value = _transpilar_codigo(codigo, selector.value)
            else:
                salida.value = _ejecutar_codigo(codigo)
        except Exception as exc:
            salida.value = _formatear_error(exc)
        finally:
            page.update()

    def tokens_handler(e):
        codigo = _normalizar_codigo(entrada.value)
        try:
            salida.value = _mostrar_tokens(codigo)
        except Exception as exc:
            salida.value = _formatear_error(exc)
        finally:
            page.update()

    def ast_handler(e):
        codigo = _normalizar_codigo(entrada.value)
        try:
            salida.value = _mostrar_ast(codigo)
        except Exception as exc:
            salida.value = _formatear_error(exc)
        finally:
            page.update()

    page.add(
        entrada,
        selector,
        activar,
        ft.ElevatedButton("Ejecutar", on_click=ejecutar_handler),
        ft.ElevatedButton("Tokens", on_click=tokens_handler),
        ft.ElevatedButton("AST", on_click=ast_handler),
        salida,
    )
