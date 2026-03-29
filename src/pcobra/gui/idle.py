"""Entorno interactivo para ejecutar código Cobra y explorar tokens y AST."""

import io
from contextlib import redirect_stderr, redirect_stdout
import flet as ft

from pcobra.cobra.core import Lexer, LexerError, Parser, ParserError
from pcobra.cobra.transpilers.target_utils import target_cli_choices
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.cobra.cli.commands.compile_cmd import TRANSPILERS


def _ejecutar_codigo(codigo: str) -> str:
    """Ejecuta código Cobra y captura la salida impresa."""
    buffer = io.StringIO()
    with redirect_stdout(buffer), redirect_stderr(buffer):
        tokens = Lexer(codigo).tokenizar()
        ast = Parser(tokens).parsear()
        InterpretadorCobra().ejecutar_ast(ast)
    return buffer.getvalue()


def _mostrar_tokens(codigo: str) -> str:
    tokens = Lexer(codigo).tokenizar()
    return "\n".join(str(t) for t in tokens)


def _mostrar_ast(codigo: str) -> str:
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    return str(ast)


def _transpilar_codigo(codigo: str, lang: str) -> str:
    """Transpila código Cobra al lenguaje especificado."""
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    transp = TRANSPILERS[lang]()
    return transp.generate_code(ast)


def _normalizar_codigo(codigo: str | None) -> str:
    """Normaliza la entrada para evitar valores ``None``."""
    return codigo or ""


def _formatear_error(exc: Exception) -> str:
    """Convierte excepciones en mensajes legibles para la GUI."""
    if isinstance(exc, LexerError):
        return f"Error léxico (línea {exc.linea}, columna {exc.columna}): {exc}"
    if isinstance(exc, ParserError):
        return f"Error de sintaxis: {exc}"
    return f"Error de ejecución: {exc}"


def _gui_target_choices() -> tuple[str, ...]:
    """Devuelve targets canónicos visibles en GUI preservando el orden oficial."""
    return target_cli_choices(set(OFFICIAL_TARGETS) & set(TRANSPILERS))


def main(page: ft.Page):
    """Función principal para el entorno IDLE."""

    entrada = ft.TextField(multiline=True, expand=True)
    salida = ft.Text(value="", selectable=True)
    lenguajes = list(_gui_target_choices())
    selector = ft.Dropdown(options=[ft.dropdown.Option(lang) for lang in lenguajes])
    activar = ft.Switch(label="Transpilar")

    def ejecutar_handler(e):
        codigo = _normalizar_codigo(entrada.value)
        try:
            if activar.value and selector.value in TRANSPILERS:
                salida.value = _transpilar_codigo(codigo, selector.value)
            else:
                salida.value = _ejecutar_codigo(codigo)
        except (LexerError, ParserError) as exc:
            salida.value = _formatear_error(exc)
        except Exception as exc:
            salida.value = _formatear_error(exc)
        finally:
            page.update()

    def tokens_handler(e):
        codigo = _normalizar_codigo(entrada.value)
        try:
            salida.value = _mostrar_tokens(codigo)
        except (LexerError, ParserError) as exc:
            salida.value = _formatear_error(exc)
        except Exception as exc:
            salida.value = _formatear_error(exc)
        finally:
            page.update()

    def ast_handler(e):
        codigo = _normalizar_codigo(entrada.value)
        try:
            salida.value = _mostrar_ast(codigo)
        except (LexerError, ParserError) as exc:
            salida.value = _formatear_error(exc)
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
