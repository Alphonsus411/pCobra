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


def main(page: ft.Page):
    """Función principal para Flet."""

    entrada = ft.TextField(multiline=True, expand=True)
    salida = ft.Text(value="", selectable=True)

    def ejecutar_handler(e):
        salida.value = _ejecutar_codigo(entrada.value)
        page.update()

    page.add(
        entrada,
        ft.ElevatedButton("Ejecutar", on_click=ejecutar_handler),
        salida,
    )
