"""Entorno interactivo para ejecutar código Cobra y explorar tokens y AST."""

import io
import sys
import flet as ft

from cobra.core import Lexer
from cobra.core import Parser
from core.interpreter import InterpretadorCobra
from cobra.cli.commands.compile_cmd import TRANSPILERS


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


def _transpilar_codigo(codigo: str, lang: str) -> str:
    """Transpila código Cobra al lenguaje especificado."""
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    transp = TRANSPILERS[lang]()
    return transp.generate_code(ast)


def main(page: ft.Page):
    """Función principal para el entorno IDLE."""

    entrada = ft.TextField(multiline=True, expand=True)
    salida = ft.Text(value="", selectable=True)
    lenguajes = sorted(TRANSPILERS.keys())
    selector = ft.Dropdown(options=[ft.dropdown.Option(lang) for lang in lenguajes])
    activar = ft.Switch(label="Transpilar")

    def ejecutar_handler(e):
        if activar.value and selector.value in TRANSPILERS:
            salida.value = _transpilar_codigo(entrada.value, selector.value)
        else:
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
        selector,
        activar,
        ft.ElevatedButton("Ejecutar", on_click=ejecutar_handler),
        ft.ElevatedButton("Tokens", on_click=tokens_handler),
        ft.ElevatedButton("AST", on_click=ast_handler),
        salida,
    )
