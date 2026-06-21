"""IDLE gráfico principal para editar, ejecutar e inspeccionar código Cobra."""

import re
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
        ft, label="Proyecto activo", value=str(project_root), expand=True
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
                entrada.value, salida.value = runtime.abrir_archivo_desde_ruta_validada(
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
            _contenido, salida.value = runtime.guardar_archivo_como_validado(
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
            runtime.flet_text(ft, value=f"Proyecto activo: {project_root}")
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

    def nombre_proyecto_seguro(texto: str) -> str:
        nombre = re.sub(r"[^A-Za-z0-9._-]+", "_", texto.strip()).strip("._-")
        if not nombre:
            raise ValueError("Indica un nombre de proyecto válido.")
        return nombre

    def resolver_directorio_proyecto(texto: str | Path) -> Path:
        ruta_texto = str(texto).strip()
        if not ruta_texto:
            raise ValueError("Indica un directorio de proyecto.")
        ruta = Path(ruta_texto)
        candidata = ruta if ruta.is_absolute() else workspace_root / ruta
        candidata = candidata.resolve()
        workspace_canonico = workspace_root.resolve()
        try:
            candidata.relative_to(workspace_canonico)
        except ValueError as exc:
            raise ValueError(
                f"El proyecto debe estar dentro de: {workspace_canonico}"
            ) from exc
        return runtime.validar_project_root_idle(candidata)

    def hay_proyecto_activo() -> bool:
        return project_root.resolve() != workspace_root.resolve()

    def requerir_proyecto_activo() -> bool:
        if hay_proyecto_activo():
            return True
        salida.value = "Crea o abre un proyecto antes de trabajar con archivos."
        page.update()
        return False

    def inicializar_estructura_proyecto(ruta_proyecto: Path, nombre: str) -> None:
        ruta_proyecto.mkdir(parents=True, exist_ok=True)
        (ruta_proyecto / "src").mkdir(parents=True, exist_ok=True)
        readme = ruta_proyecto / "README.md"
        if not readme.exists():
            readme.write_text(f"# {nombre}\n", encoding="utf-8")

    def crear_proyecto_handler(_e):
        nonlocal project_root
        try:
            nombre = nombre_proyecto_seguro(raiz_input.value or "")
            nuevo_proyecto = (workspace_root / nombre).resolve()
            inicializar_estructura_proyecto(nuevo_proyecto, nombre)
        except (OSError, ValueError) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return
        project_root = nuevo_proyecto
        if not reconstruir_arbol():
            page.update()
            return
        salida.value = f"Proyecto creado: {project_root}"
        actualizar_pagina()

    def establecer_raiz_arbol_handler(_e):
        nonlocal project_root
        try:
            nueva_raiz = resolver_directorio_proyecto(raiz_input.value or "")
        except (OSError, ValueError) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return
        if not nueva_raiz.is_dir():
            salida.value = f"El proyecto activo debe ser un directorio: {nueva_raiz}"
            page.update()
            return
        try:
            inicializar_estructura_proyecto(nueva_raiz, nueva_raiz.name)
        except OSError as exc:
            mostrar_error_archivo(exc)
            page.update()
            return
        project_root = nueva_raiz
        if not reconstruir_arbol():
            page.update()
            return
        salida.value = f"Proyecto abierto: {project_root}"
        actualizar_pagina()

    def nuevo_handler(_e):
        entrada.value, salida.value = runtime.crear_archivo_nuevo_en_editor(estado)
        actualizar_pagina()

    def abrir_handler(_e):
        if not requerir_proyecto_activo():
            return

        ruta = validar_ruta_visible_para_abrir()
        if ruta is None:
            return

        cargar_archivo(ruta)

    def guardar_handler(_e):

        if not requerir_proyecto_activo():
            return

        if estado.ruta is None:
            guardar_como_handler(_e)
            return
        ruta_resuelta = resolver_ruta_archivo_idle(estado.ruta)
        if ruta_resuelta is None:
            return
        estado.ruta = ruta_resuelta
        try:
            _contenido, salida.value = runtime.guardar_archivo_activo_validado(
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
        if not requerir_proyecto_activo():
            return

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

        if not requerir_proyecto_activo():
            return

        if estado.ruta is None:
            salida.value = "No hay archivo activo que recargar."
            page.update()
            return
        ruta_resuelta = resolver_ruta_archivo_idle(estado.ruta)
        if ruta_resuelta is None:
            return
        estado.ruta = ruta_resuelta
        try:
            entrada.value, salida.value = runtime.recargar_archivo_activo_validado(estado)
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

    barra_raiz_arbol = runtime.flet_column(
        ft,
        controls=[
            raiz_input,
            runtime.flet_row(
                ft,
                controls=[
                    runtime.flet_elevated_button(
                        ft, "Crear proyecto", on_click=crear_proyecto_handler
                    ),
                    runtime.flet_elevated_button(
                        ft, "Abrir proyecto", on_click=establecer_raiz_arbol_handler
                    ),
                ],
                wrap=True,
            ),
        ],
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
