"""Entorno interactivo para ejecutar código Cobra y explorar tokens y AST."""

from typing import TYPE_CHECKING

from pcobra.gui import runtime

if TYPE_CHECKING:
    import flet as ft


def main(page: "ft.Page"):
    """Función principal para el entorno IDLE."""
    ft = runtime.require_flet()

    entrada = ft.TextField(multiline=True, expand=True)
    salida = ft.Text(value="", selectable=True)
    lenguajes = list(runtime.gui_target_choices())
    selector = ft.Dropdown(options=[ft.dropdown.Option(lang) for lang in lenguajes])
    activar = ft.Switch(label="Transpilar")

    def ejecutar_handler(_e):
        deps = runtime.require_gui_dependencies()
        codigo = runtime.normalizar_codigo(entrada.value)
        try:
            if activar.value and selector.value in deps["TRANSPILERS"]:
                salida.value = runtime.transpilar_codigo(codigo, selector.value)
            else:
                salida.value = runtime.ejecutar_codigo(codigo)
        except Exception as exc:
            salida.value = runtime.formatear_error(exc)
        finally:
            page.update()

    def tokens_handler(_e):
        codigo = runtime.normalizar_codigo(entrada.value)
        try:
            salida.value = runtime.mostrar_tokens(codigo)
        except Exception as exc:
            salida.value = runtime.formatear_error(exc)
        finally:
            page.update()

    def ast_handler(_e):
        codigo = runtime.normalizar_codigo(entrada.value)
        try:
            salida.value = runtime.mostrar_ast(codigo)
        except Exception as exc:
            salida.value = runtime.formatear_error(exc)
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
