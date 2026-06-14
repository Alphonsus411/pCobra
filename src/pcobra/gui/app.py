"""Aplicación gráfica básica usando Flet para ejecutar código Cobra."""

from typing import TYPE_CHECKING

from pcobra.gui import runtime

if TYPE_CHECKING:
    import flet as ft


def main(page: "ft.Page"):
    """Interfaz mínima de Flet basada en componentes compartidos."""
    ft = runtime.require_flet()

    lenguajes = list(runtime.gui_target_choices())
    estado_archivo = runtime.GuiFileState()

    entrada = runtime.crear_editor_codigo(ft)
    salida = runtime.crear_salida_seleccionable(ft)
    selector = runtime.crear_selector_target(ft, lenguajes=lenguajes)
    activar = runtime.crear_switch_transpilacion(ft, lenguajes=lenguajes)

    guardar_handler = runtime.crear_handler_guardar(
        entrada=entrada,
        estado_archivo=estado_archivo,
        page=page,
    )
    guardar_como_handler = runtime.crear_handler_guardar_como(
        entrada=entrada,
        estado_archivo=estado_archivo,
        page=page,
    )
    ejecutar_handler = runtime.crear_handler_ejecucion(
        entrada=entrada,
        salida=salida,
        selector=selector,
        activar=activar,
        page=page,
    )
    sugerencias_agix_handler = runtime.crear_handler_sugerencias_agix(
        entrada=entrada,
        salida=salida,
        page=page,
    )

    def cargar_archivo_handler(e):
        if e.control.data and runtime.es_archivo_cobra(e.control.data):
            ruta_archivo = e.control.data
            entrada.value = runtime.leer_archivo_texto(ruta_archivo)
            estado_archivo.ruta = ruta_archivo
            estado_archivo.contenido_cargado = entrada.value
            estado_archivo.cambios_sin_guardar = False
            page.update()

    arbol_directorios = runtime.crear_arbol_directorios(ft, on_click=cargar_archivo_handler, root_path=Path(".").resolve())

    page.add(
        runtime.flet_row(
            ft,
            [
                runtime.flet_elevated_button(ft, "Guardar", on_click=guardar_handler),
                runtime.flet_elevated_button(ft, "Guardar como", on_click=guardar_como_handler),
                selector,
                activar,
                runtime.flet_elevated_button(ft, "Ejecutar", on_click=ejecutar_handler),
                runtime.flet_elevated_button(ft, "Sugerencias (Agix)", on_click=sugerencias_agix_handler),
            ]
        ),
        runtime.flet_row(
            ft,
            [
                runtime.flet_column(ft, [arbol_directorios], expand=1),
                runtime.flet_column(ft, [entrada, salida], expand=4),
            ],
            expand=True,
        ),
    )

if __name__ == "__main__":
    runtime.flet_app(main)
