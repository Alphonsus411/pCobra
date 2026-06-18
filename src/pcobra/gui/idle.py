"""IDLE gráfico principal para editar, ejecutar e inspeccionar código Cobra."""

from pathlib import Path
from typing import TYPE_CHECKING

from pcobra.gui import runtime

if TYPE_CHECKING:
    import flet as ft


def main(page: "ft.Page"):
    """Interfaz principal del IDLE con archivos, árbol, ejecución, tokens, AST y sugerencias."""
    ft = runtime.require_flet()

    estado = runtime.GuiFileState()
    directorio_actual = Path.cwd().resolve()

    entrada = runtime.crear_editor_codigo(ft)
    salida = runtime.crear_salida_seleccionable(ft)
    estado_archivo = runtime.flet_text(ft, value=runtime.crear_titulo_archivo(estado))
    ruta_input = runtime.flet_text_field(ft, label="Ruta", value="", expand=True)
    arbol = runtime.flet_list_view(ft, expand=True, spacing=2, auto_scroll=False)
    lenguajes = list(runtime.gui_target_choices())
    selector = runtime.crear_selector_target(ft, lenguajes=lenguajes)
    activar = runtime.crear_switch_transpilacion(ft, lenguajes=lenguajes)

    def sincronizar_estado_visual() -> None:
        estado_archivo.value = runtime.crear_titulo_archivo(estado)
        ruta_input.value = str(estado.ruta or "")

    def actualizar_pagina() -> None:
        sincronizar_estado_visual()
        page.update()

    def marcar_cambios(_e=None) -> None:
        runtime.marcar_cambios_editor(estado, entrada.value)
        actualizar_pagina()

    entrada.on_change = marcar_cambios

    def mostrar_error_archivo(exc: Exception) -> None:
        salida.value = runtime.formatear_error(exc)

    def cargar_archivo(ruta: Path, *, desde_arbol: bool = False) -> None:
        nonlocal directorio_actual
        try:
            if desde_arbol:
                entrada.value, salida.value = runtime.cargar_archivo_desde_arbol(
                    ruta, estado
                )
            else:
                entrada.value, salida.value = runtime.abrir_archivo_desde_ruta(
                    ruta, estado
                )
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            UnicodeError,
            ValueError,
        ) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return
        directorio_actual = estado.ruta.parent if estado.ruta else directorio_actual
        reconstruir_arbol()
        actualizar_pagina()

    def guardar_en(ruta: Path) -> bool:
        try:
            _contenido, salida.value = runtime.guardar_archivo_como(
                ruta, entrada.value, estado
            )
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            UnicodeError,
            ValueError,
        ) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return False
        reconstruir_arbol()
        actualizar_pagina()
        return True

    def cargar_archivo_desde_evento_arbol(e) -> None:
        control = getattr(e, "control", None)
        ruta = getattr(control, "data", None)
        if ruta is None:
            salida.value = "No se pudo determinar la ruta seleccionada en el árbol."
            page.update()
            return
        cargar_archivo(Path(ruta), desde_arbol=True)

    def reconstruir_arbol() -> None:
        arbol.controls.clear()
        arbol.controls.append(
            runtime.flet_text(ft, value=f"Directorio raíz: {directorio_actual}")
        )
        try:
            arbol_canonico = runtime.crear_arbol_directorios(
                ft,
                on_click=cargar_archivo_desde_evento_arbol,
                root_path=directorio_actual,
            )
        except (FileNotFoundError, NotADirectoryError, PermissionError) as exc:
            mostrar_error_archivo(exc)
            return
        arbol.controls.extend(getattr(arbol_canonico, "controls", [arbol_canonico]))

    def nuevo_handler(_e):
        entrada.value, salida.value = runtime.crear_archivo_nuevo_en_editor(estado)
        actualizar_pagina()

    def abrir_handler(_e):
        if not ruta_input.value:
            salida.value = (
                "Indica una ruta para abrir o selecciona un archivo del árbol."
            )
            page.update()
            return
        cargar_archivo(Path(ruta_input.value))

    def guardar_handler(_e):
        if estado.ruta is None:
            guardar_como_handler(_e)
            return
        try:
            _contenido, salida.value = runtime.guardar_archivo_activo(
                entrada.value, estado
            )
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            UnicodeError,
            ValueError,
        ) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return
        reconstruir_arbol()
        actualizar_pagina()

    def guardar_como_handler(_e):
        if not ruta_input.value:
            salida.value = "Indica una ruta de destino en el campo Ruta."
            page.update()
            return
        guardar_en(Path(ruta_input.value))

    def recargar_handler(_e):
        if estado.ruta is None:
            salida.value = "No hay archivo activo que recargar."
            page.update()
            return
        try:
            entrada.value, salida.value = runtime.recargar_archivo_activo(estado)
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            UnicodeError,
            ValueError,
        ) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return
        reconstruir_arbol()
        actualizar_pagina()

    ejecutar_handler = runtime.crear_handler_ejecucion(
        entrada=entrada, salida=salida, selector=selector, activar=activar, page=page
    )
    tokens_handler = runtime.crear_handler_tokens(
        entrada=entrada, salida=salida, page=page
    )
    ast_handler = runtime.crear_handler_ast(entrada=entrada, salida=salida, page=page)
    sugerencias_handler = runtime.crear_handler_sugerencias(
        entrada=entrada, salida=salida, page=page
    )

    reconstruir_arbol()
    sincronizar_estado_visual()

    barra_archivo = runtime.flet_row(
        ft,
        controls=[
            runtime.flet_elevated_button(ft, "Nuevo", on_click=nuevo_handler),
            runtime.flet_elevated_button(ft, "Abrir", on_click=abrir_handler),
            runtime.flet_elevated_button(ft, "Guardar", on_click=guardar_handler),
            runtime.flet_elevated_button(
                ft, "Guardar como", on_click=guardar_como_handler
            ),
            runtime.flet_elevated_button(ft, "Recargar", on_click=recargar_handler),
        ],
        wrap=True,
    )
    barra_ejecucion = runtime.flet_row(
        ft,
        controls=[
            selector,
            activar,
            runtime.flet_elevated_button(ft, "Ejecutar", on_click=ejecutar_handler),
            runtime.flet_elevated_button(ft, "Tokens", on_click=tokens_handler),
            runtime.flet_elevated_button(ft, "AST", on_click=ast_handler),
            runtime.crear_boton_sugerencias_libro(
                ft, on_click=sugerencias_handler
            ),
        ],
        wrap=True,
    )
    editor = runtime.flet_column(
        ft,
        controls=[
            estado_archivo,
            ruta_input,
            barra_archivo,
            entrada,
            barra_ejecucion,
            salida,
        ],
        expand=True,
    )
    panel_lateral = runtime.flet_container(
        ft,
        content=runtime.flet_column(
            ft,
            controls=[runtime.flet_text(ft, value="Archivos Cobra"), arbol],
            expand=True,
        ),
        width=280,
    )

    page.add(runtime.flet_row(ft, controls=[panel_lateral, editor], expand=True))


if __name__ == "__main__":
    runtime.flet_app(main)
