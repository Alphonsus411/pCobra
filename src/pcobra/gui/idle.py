"""Entorno interactivo para ejecutar código Cobra y explorar tokens y AST."""

from typing import TYPE_CHECKING

from pcobra.gui import runtime

if TYPE_CHECKING:
    import flet as ft


def main(page: "ft.Page"):
    """Función principal para el entorno IDLE."""
    ft = runtime.require_flet()

    entrada = runtime.flet_text_field(ft, multiline=True, expand=True)
    salida = runtime.flet_text(ft, value="", selectable=True)
    lenguajes = list(runtime.gui_target_choices())
    selector = runtime.flet_dropdown(
        ft, options=[runtime.flet_dropdown_option(ft, lang) for lang in lenguajes]
    )
    if lenguajes:
        selector.value = lenguajes[0]

    activar = runtime.flet_switch(ft, label="Transpilar", disabled=not lenguajes)

    def ejecutar_handler(_e):
        deps = runtime.require_gui_dependencies()
        codigo = runtime.normalizar_codigo(entrada.value)
        try:
            if activar.value and selector.value not in deps["TRANSPILERS"]:
                salida.value = "Selecciona un lenguaje destino para transpilar"
            elif activar.value and selector.value in deps["TRANSPILERS"]:
                salida.value = runtime.transpilar_codigo(codigo, selector.value)
            else:
                salida.value = runtime.ejecutar_codigo(codigo)
        except Exception as exc:
            salida.value = runtime.formatear_error(
                exc,
                lexer_error_type=deps.get("LexerError"),
                parser_error_type=deps.get("ParserError"),
            )
        finally:
            page.update()

    def tokens_handler(_e):
        deps = runtime.require_gui_dependencies()
        codigo = runtime.normalizar_codigo(entrada.value)
        try:
            salida.value = runtime.mostrar_tokens(codigo)
        except Exception as exc:
            salida.value = runtime.formatear_error(
                exc,
                lexer_error_type=deps.get("LexerError"),
                parser_error_type=deps.get("ParserError"),
            )
        finally:
            page.update()

    def ast_handler(_e):
        deps = runtime.require_gui_dependencies()
        codigo = runtime.normalizar_codigo(entrada.value)
        try:
            salida.value = runtime.mostrar_ast(codigo)
        except Exception as exc:
            salida.value = runtime.formatear_error(
                exc,
                lexer_error_type=deps.get("LexerError"),
                parser_error_type=deps.get("ParserError"),
            )
        finally:
            page.update()

    page.add(
        entrada,
        selector,
        activar,
        runtime.flet_elevated_button(ft, "Ejecutar", on_click=ejecutar_handler),
        runtime.flet_elevated_button(ft, "Tokens", on_click=tokens_handler),
        runtime.flet_elevated_button(ft, "AST", on_click=ast_handler),
        salida,
    )
