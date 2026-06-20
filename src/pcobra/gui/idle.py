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
    workspace_root = runtime.resolver_workspace_root_idle()
    project_root = workspace_root

    entrada = runtime.crear_editor_codigo(ft)
    salida = runtime.crear_salida_seleccionable(ft)
    estado_archivo = runtime.flet_text(ft, value=runtime.crear_titulo_archivo(estado))
    # Flujo canónico del IDLE: el campo Ruta es la fuente visible para abrir y
    # para Guardar como. ``runtime.crear_handler_guardar_como`` queda reservado
    # como helper FilePicker para integraciones alternativas de Flet.
    ruta_input = runtime.flet_text_field(ft, label="Ruta", value="", expand=True)
    raiz_input = runtime.flet_text_field(
        ft, label="Raíz del árbol", value=str(project_root), expand=True
    )
    arbol = runtime.flet_list_view(ft, expand=True, spacing=2, auto_scroll=False)
    lenguajes = list(runtime.gui_target_choices())
    selector = runtime.crear_selector_target(ft, lenguajes=lenguajes)
    activar = runtime.crear_switch_transpilacion(ft, lenguajes=lenguajes)

    def sincronizar_estado_visual() -> None:
        estado_archivo.value = runtime.crear_titulo_archivo(estado)

        if estado.ruta is not None:
            ruta_input.value = str(estado.ruta)

    def actualizar_pagina() -> None:
        sincronizar_estado_visual()
        page.update()

    def marcar_cambios(_e=None) -> None:
        runtime.marcar_cambios_editor(estado, entrada.value)
        actualizar_pagina()

    entrada.on_change = marcar_cambios

    def mostrar_error_archivo(exc: Exception) -> None:
        salida.value = runtime.formatear_error(exc)

    def resolver_ruta_archivo_idle(ruta: str | Path) -> Path | None:
        try:
            return runtime.resolver_ruta_archivo_en_project_root(ruta, project_root)
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            ValueError,
        ) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return None

    def validar_ruta_visible_para_abrir() -> Path | None:
        """Valida la ruta visible antes de abrirla desde el IDLE.

        El campo ``ruta_input`` es la fuente canónica de la acción Abrir. Por
        eso se resuelve siempre contra ``project_root`` antes de delegar en el
        runtime de archivos: rutas relativas quedan ancladas al proyecto, rutas
        absolutas deben pertenecer a él y la resolución canónica bloquea
        ``..`` o symlinks externos.
        """

        texto = (ruta_input.value or "").strip()

        if not texto:
            salida.value = "Indica la ruta de un archivo Cobra."
            page.update()
            return None

        return resolver_ruta_archivo_idle(texto)

    def cargar_archivo(ruta: Path, *, desde_arbol: bool = False) -> None:
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
        # Abrir un archivo solo cambia el archivo activo (estado.ruta). La raíz
        # visible del árbol permanece anclada a project_root para no contraer el
        # explorador al directorio padre del archivo abierto.
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
        ruta_resuelta = resolver_ruta_archivo_idle(Path(ruta))
        if ruta_resuelta is None:
            return
        cargar_archivo(ruta_resuelta, desde_arbol=True)

    def reconstruir_arbol() -> bool:
        raiz_input.value = str(project_root)
        arbol.controls.clear()
        arbol.controls.append(
            runtime.flet_text(ft, value=f"Directorio raíz: {project_root}")
        )
        try:
            arbol_canonico = runtime.crear_arbol_directorios(
                ft,
                on_click=cargar_archivo_desde_evento_arbol,
                root_path=project_root,
            )
        except (FileNotFoundError, NotADirectoryError, PermissionError) as exc:
            mostrar_error_archivo(exc)
            arbol.controls.append(
                runtime.flet_text(
                    ft,
                    value=f"No se pudo listar la ruta: {runtime.formatear_error(exc)}",
                )
            )
            return False
        arbol.controls.extend(getattr(arbol_canonico, "controls", [arbol_canonico]))
        return True

    def establecer_raiz_arbol_handler(_e):
        nonlocal project_root
        if not raiz_input.value:
            salida.value = "Indica un directorio para usar como raíz del árbol."
            page.update()
            return
        try:
            nueva_raiz = runtime.normalizar_ruta_archivo_gui(raiz_input.value)
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            ValueError,
        ) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return
        if not nueva_raiz.is_dir():
            salida.value = f"La raíz del árbol debe ser un directorio: {nueva_raiz}"
            page.update()
            return
        project_root = nueva_raiz
        if not reconstruir_arbol():
            page.update()
            return
        salida.value = f"Raíz del árbol actualizada: {project_root}"
        actualizar_pagina()

    def nuevo_handler(_e):
        entrada.value, salida.value = runtime.crear_archivo_nuevo_en_editor(estado)
        actualizar_pagina()

    def abrir_handler(_e):
        ruta = validar_ruta_visible_para_abrir()
        if ruta is None:
            return

        cargar_archivo(ruta)

    def guardar_handler(_e):
        if estado.ruta is None:
            guardar_como_handler(_e)
            return
        ruta_resuelta = resolver_ruta_archivo_idle(estado.ruta)
        if ruta_resuelta is None:
            return
        estado.ruta = ruta_resuelta
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
        """Guarda usando el campo Ruta, flujo canónico del IDLE principal."""
        texto = (ruta_input.value or "").strip()

        if not texto:
            salida.value = "Indica la ruta de un archivo Cobra."
            page.update()
            return

        ruta = resolver_ruta_archivo_idle(texto)
        if ruta is None:
            return

        if guardar_en(ruta):
            ruta_input.value = str(ruta)
            page.update()

    def recargar_handler(_e):
        if estado.ruta is None:
            salida.value = "No hay archivo activo que recargar."
            page.update()
            return
        ruta_resuelta = resolver_ruta_archivo_idle(estado.ruta)
        if ruta_resuelta is None:
            return
        estado.ruta = ruta_resuelta
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
    correccion_handler = runtime.crear_handler_correccion_tipografica(
        entrada=entrada, salida=salida, page=page
    )

    reconstruir_arbol()
    sincronizar_estado_visual()

    barra_raiz_arbol = runtime.flet_row(
        ft,
        controls=[
            raiz_input,
            runtime.flet_elevated_button(
                ft, "Establecer raíz", on_click=establecer_raiz_arbol_handler
            ),
        ],
        wrap=True,
    )

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
            runtime.crear_boton_sugerencias_libro(ft, on_click=sugerencias_handler),
            runtime.crear_boton_correccion(ft, on_click=correccion_handler),
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
            controls=[
                runtime.flet_text(ft, value="Archivos Cobra"),
                barra_raiz_arbol,
                arbol,
            ],
            expand=True,
        ),
        width=280,
        padding=12,
        border_radius=8,
    )

    page.add(runtime.flet_row(ft, controls=[panel_lateral, editor], expand=True))


if __name__ == "__main__":
    runtime.flet_app(main)
