import io
import sys
import flet as ft

from backend.src.cobra.lexico.lexer import Lexer
from backend.src.cobra.parser.parser import Parser
from backend.src.core.interpreter import InterpretadorCobra


def _ejecutar_codigo(codigo: str) -> str:
    """Ejecuta código Cobra y captura la salida impresa."""
    buffer = io.StringIO()
    stdout = sys.stdout
    sys.stdout = buffer
    try:
        tokens = Lexer(codigo).tokenizar()
        ast = Parser(tokens).parsear()
        InterpretadorCobra().ejecutar_ast(ast)
    finally:
        sys.stdout = stdout
    return buffer.getvalue()


def _mostrar_tokens(codigo: str) -> str:
    tokens = Lexer(codigo).tokenizar()
    return "\n".join(str(t) for t in tokens)


def _mostrar_ast(codigo: str) -> str:
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    return str(ast)


def main(page: ft.Page):
    """Función principal para el entorno IDLE."""

    entrada = ft.TextField(multiline=True, expand=True)
    salida = ft.Text(value="", selectable=True)

    def ejecutar_handler(e):
        salida.value = _ejecutar_codigo(entrada.value)
        page.update()

    def tokens_handler(e):
        salida.value = _mostrar_tokens(entrada.value)
        page.update()

    def ast_handler(e):
        salida.value = _mostrar_ast(entrada.value)
        page.update()

    page.add(
        entrada,
        ft.ElevatedButton("Ejecutar", on_click=ejecutar_handler),
        ft.ElevatedButton("Tokens", on_click=tokens_handler),
        ft.ElevatedButton("AST", on_click=ast_handler),
        salida,
    )
