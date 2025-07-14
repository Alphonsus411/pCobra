"""Aplicación gráfica básica usando Flet para ejecutar código Cobra."""

import io
import sys
import flet as ft

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.interpreter import InterpretadorCobra


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
