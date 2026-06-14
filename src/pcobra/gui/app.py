"""Aplicación gráfica básica usando Flet para ejecutar código Cobra."""

from typing import TYPE_CHECKING

from pcobra.gui import runtime

if TYPE_CHECKING:
    import flet as ft


def main(page: "ft.Page"):
    """Interfaz mínima de Flet basada en componentes compartidos."""
    ft = runtime.require_flet()

    lenguajes = list(runtime.gui_target_choices())
    entrada = runtime.crear_editor_codigo(ft)
    salida = runtime.crear_salida_seleccionable(ft)
    selector = runtime.crear_selector_target(ft, lenguajes=lenguajes)
    activar = runtime.crear_switch_transpilacion(ft, lenguajes=lenguajes)
    ejecutar_handler = runtime.crear_handler_ejecucion(
        entrada=entrada,
        salida=salida,
        selector=selector,
        activar=activar,
        page=page,
    )

    page.add(
        entrada,
        selector,
        activar,
        runtime.flet_elevated_button(ft, "Ejecutar", on_click=ejecutar_handler),
        salida,
    )

if __name__ == "__main__":
    runtime.flet_app(main)
