"""IDLE gráfico principal para editar, ejecutar e inspeccionar código Cobra."""

import re
from pathlib import Path
from typing import TYPE_CHECKING

from pcobra.gui import runtime

if TYPE_CHECKING:
    import flet as ft


def resolver_ruta_en_project_root(ruta: str | Path, project_root: str | Path) -> Path:
    """Resuelve ``ruta`` de forma canónica y exige que quede bajo ``project_root``."""

    project_root_resuelto = Path(project_root).expanduser().resolve()
    ruta_expandida = Path(ruta).expanduser()
    candidata = (
        ruta_expandida
        if ruta_expandida.is_absolute()
        else project_root_resuelto / ruta_expandida
    )
    candidata = candidata.resolve()
    try:
        candidata.relative_to(project_root_resuelto)
    except ValueError as exc:
        raise ValueError(
            f"La ruta debe estar dentro del proyecto activo: {project_root_resuelto}"
        ) from exc
    return candidata


def validar_ruta_carpeta_eliminable_idle(
    ruta: str | Path, project_root: str | Path, workspace_root: str | Path
) -> Path:
    """Valida una carpeta visible antes de permitir su eliminación desde el IDLE."""

    ruta_resuelta = resolver_ruta_en_project_root(ruta, project_root)
    project_root_resuelto = Path(project_root).resolve()
    workspace_root_resuelto = Path(workspace_root).resolve()

    if ruta_resuelta == project_root_resuelto:
        raise ValueError(
            "No se puede eliminar el proyecto activo como carpeta normal. "
            'Usa "Eliminar proyecto".'
        )

    if ruta_resuelta == workspace_root_resuelto:
        raise ValueError("No se puede eliminar la raíz completa del workspace.")

    return ruta_resuelta


def validar_project_root_eliminable_idle(
    project_root: str | Path, workspace_root: str | Path
) -> Path:
    """Valida el proyecto activo antes de permitir su eliminación desde el IDLE."""

    project_root_resuelto = Path(project_root).resolve()
    workspace_root_resuelto = Path(workspace_root).resolve()

    if project_root_resuelto == workspace_root_resuelto:
        raise ValueError("No se puede eliminar la raíz completa del workspace.")

    if project_root_resuelto.parent != workspace_root_resuelto:
        raise ValueError(
            "La raíz del proyecto debe ser hija directa de la raíz del workspace."
        )

    if not project_root_resuelto.exists():
        raise FileNotFoundError(
            f"No existe el proyecto que se quiere eliminar: {project_root_resuelto}"
        )

    if not project_root_resuelto.is_dir():
        raise NotADirectoryError(
            f"La ruta del proyecto no es un directorio: {project_root_resuelto}"
        )

    return project_root_resuelto


def main(page: "ft.Page"):
    """Interfaz principal del IDLE con archivos, árbol, ejecución, tokens, AST y sugerencias."""
    ft = runtime.require_flet()

    estado = runtime.GuiFileState()
    workspace_root = runtime.resolver_workspace_root_idle()
    project_root = workspace_root
    proyecto_cerrado = False

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
    confirmacion_eliminacion_archivo_pendiente: dict[str, object] | None = None
    confirmacion_eliminacion_carpeta_pendiente: dict[str, object] | None = None

    def cancelar_confirmacion_eliminacion_pendiente() -> None:
        nonlocal confirmacion_eliminacion_archivo_pendiente
        confirmacion_eliminacion_archivo_pendiente = None

    def cancelar_confirmacion_carpeta_eliminacion_pendiente() -> None:
        nonlocal confirmacion_eliminacion_carpeta_pendiente
        confirmacion_eliminacion_carpeta_pendiente = None

    def cancelar_confirmaciones_eliminacion_pendientes() -> None:
        cancelar_confirmacion_eliminacion_pendiente()
        cancelar_confirmacion_carpeta_eliminacion_pendiente()

    def sincronizar_estado_visual() -> None:
        estado_archivo.value = runtime.crear_titulo_archivo(estado)

        if estado.ruta is not None:
            ruta_input.value = str(estado.ruta)

    def limpiar_archivo_activo() -> None:
        cancelar_confirmaciones_eliminacion_pendientes()
        estado.ruta = None
        estado.contenido_cargado = ""
        estado.cambios_sin_guardar = False
        entrada.value = ""
        ruta_input.value = ""

    def actualizar_pagina() -> None:
        sincronizar_estado_visual()
        page.update()

    def cancelar_confirmacion_si_cambia_ruta_pendiente() -> None:
        if confirmacion_eliminacion_archivo_pendiente is None:
            return
        if (
            estado.ruta != confirmacion_eliminacion_archivo_pendiente["ruta_estado"]
            or (ruta_input.value or "")
            != confirmacion_eliminacion_archivo_pendiente["ruta_visible"]
        ):
            cancelar_confirmacion_eliminacion_pendiente()

    def cancelar_confirmacion_carpeta_si_cambia_ruta_pendiente() -> None:
        if confirmacion_eliminacion_carpeta_pendiente is None:
            return
        if (
            confirmacion_eliminacion_carpeta_pendiente["tipo"] != "carpeta"
            or (ruta_input.value or "")
            != confirmacion_eliminacion_carpeta_pendiente["ruta_visible"]
        ):
            cancelar_confirmacion_carpeta_eliminacion_pendiente()

    def ruta_visible_cambiada(_e=None) -> None:
        cancelar_confirmacion_si_cambia_ruta_pendiente()
        cancelar_confirmacion_carpeta_si_cambia_ruta_pendiente()

    ruta_input.on_change = ruta_visible_cambiada

    def marcar_cambios(_e=None) -> None:
        runtime.marcar_cambios_editor(estado, entrada.value)
        actualizar_pagina()

    entrada.on_change = marcar_cambios

    def mostrar_error_archivo(exc: Exception) -> None:
        salida.value = runtime.formatear_error(exc)

    def resolver_ruta_archivo_idle(ruta: str | Path) -> Path | None:
        try:
            return runtime.resolver_ruta_texto_en_project_root(ruta, project_root)
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
            salida.value = "Indica la ruta de un archivo de texto del proyecto."
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

    def formatear_estado_workspace_proyecto() -> str:
        workspace_resuelto = workspace_root.resolve()
        project_resuelto = project_root.resolve()
        lineas = [f"Workspace: {workspace_resuelto}"]
        if project_resuelto == workspace_resuelto:
            lineas.append("Proyecto activo: ninguno")
        else:
            lineas.append(f"Proyecto activo: {project_resuelto.name}")
            lineas.append(f"Ruta completa: {project_resuelto}")
        return "\n".join(lineas)

    estado_workspace_proyecto = runtime.flet_text(
        ft, value=formatear_estado_workspace_proyecto()
    )

    def reconstruir_arbol() -> bool:
        raiz_input.value = str(project_root)
        estado_workspace_proyecto.value = formatear_estado_workspace_proyecto()
        arbol.controls.clear()
        arbol.controls.append(estado_workspace_proyecto)
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
        return not proyecto_cerrado

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
        nonlocal project_root, proyecto_cerrado
        try:
            nombre = nombre_proyecto_seguro(raiz_input.value or "")
            nuevo_proyecto = (workspace_root / nombre).resolve()
            inicializar_estructura_proyecto(nuevo_proyecto, nombre)
        except (OSError, ValueError) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return
        project_root = nuevo_proyecto
        proyecto_cerrado = False
        if not reconstruir_arbol():
            page.update()
            return
        salida.value = f"Proyecto creado: {project_root}"
        actualizar_pagina()

    def establecer_raiz_arbol_handler(_e):
        nonlocal project_root, proyecto_cerrado
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
        proyecto_cerrado = False
        if not reconstruir_arbol():
            page.update()
            return
        salida.value = f"Proyecto abierto: {project_root}"
        actualizar_pagina()

    def cerrar_proyecto_handler(_e):
        nonlocal project_root, proyecto_cerrado
        if project_root.resolve() == workspace_root.resolve():
            salida.value = "No hay proyecto activo para cerrar."
            page.update()
            return

        project_root = workspace_root
        proyecto_cerrado = True
        limpiar_archivo_activo()
        estado_archivo.value = "Archivo nuevo (sin guardar)"
        reconstruir_arbol()
        raiz_input.value = str(project_root)
        salida.value = "Proyecto cerrado."
        actualizar_pagina()

    def eliminar_proyecto_handler(_e):
        nonlocal project_root, proyecto_cerrado
        workspace_root_resuelto = workspace_root.resolve()

        if not hay_proyecto_activo():
            salida.value = "No hay proyecto activo para eliminar."
            page.update()
            return

        try:
            project_root_resuelto = validar_project_root_eliminable_idle(
                project_root, workspace_root
            )
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            OSError,
            ValueError,
        ) as exc:
            if project_root.resolve() == workspace_root_resuelto:
                salida.value = "No hay proyecto activo para eliminar."
            else:
                mostrar_error_archivo(exc)
            page.update()
            return

        nombre_proyecto = project_root_resuelto.name
        confirmacion = ruta_input.value or ""
        if confirmacion != nombre_proyecto:
            salida.value = (
                "Para eliminar este proyecto escribe su nombre exacto: "
                f"{nombre_proyecto}"
            )
            page.update()
            return

        try:
            runtime.eliminar_proyecto_validado(
                project_root_resuelto, workspace_root_resuelto
            )
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            OSError,
            ValueError,
        ) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return

        proyecto_eliminado = project_root_resuelto
        project_root = workspace_root
        proyecto_cerrado = True
        limpiar_archivo_activo()
        reconstruir_arbol()
        raiz_input.value = str(project_root)
        salida.value = f"Proyecto eliminado: {proyecto_eliminado}"
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
            salida.value = "Indica la ruta de un archivo de texto del proyecto."
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
            entrada.value, salida.value = runtime.recargar_archivo_activo_validado(
                estado
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

    def eliminar_archivo_handler(_e):
        nonlocal confirmacion_eliminacion_archivo_pendiente

        cancelar_confirmacion_si_cambia_ruta_pendiente()

        if not requerir_proyecto_activo():
            return

        if estado.ruta is None:
            cancelar_confirmacion_eliminacion_pendiente()
            salida.value = "No hay archivo activo para eliminar."
            page.update()
            return
        ruta_resuelta = resolver_ruta_archivo_idle(estado.ruta)
        if ruta_resuelta is None:
            cancelar_confirmacion_eliminacion_pendiente()
            return

        if (
            confirmacion_eliminacion_archivo_pendiente is None
            or confirmacion_eliminacion_archivo_pendiente["tipo"] != "archivo"
            or confirmacion_eliminacion_archivo_pendiente["ruta"] != ruta_resuelta
        ):
            confirmacion_eliminacion_archivo_pendiente = {
                "tipo": "archivo",
                "ruta": ruta_resuelta,
                "ruta_estado": estado.ruta,
                "ruta_visible": ruta_input.value or "",
            }
            salida.value = (
                "Pulsa de nuevo Eliminar archivo para confirmar: " f"{ruta_resuelta}"
            )
            page.update()
            return

        try:
            runtime.eliminar_archivo_validado(ruta_resuelta)
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            OSError,
            ValueError,
        ) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return
        limpiar_archivo_activo()
        reconstruir_arbol()
        salida.value = f"Archivo eliminado: {ruta_resuelta}"
        actualizar_pagina()

    def eliminar_carpeta_handler(_e):
        nonlocal confirmacion_eliminacion_carpeta_pendiente

        cancelar_confirmacion_carpeta_si_cambia_ruta_pendiente()

        if not requerir_proyecto_activo():
            return

        texto = (ruta_input.value or "").strip()

        if not texto:
            cancelar_confirmacion_carpeta_eliminacion_pendiente()
            salida.value = "Indica la ruta de una carpeta."
            page.update()
            return

        try:
            ruta_resuelta = validar_ruta_carpeta_eliminable_idle(
                texto, project_root, workspace_root
            )
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            OSError,
            ValueError,
        ) as exc:
            if str(exc).startswith(
                "No se puede eliminar el proyecto activo como carpeta normal."
            ):
                salida.value = str(exc)
            else:
                mostrar_error_archivo(exc)
            page.update()
            return

        if not ruta_resuelta.exists():
            salida.value = (
                f"No existe la carpeta que se quiere eliminar: {ruta_resuelta}"
            )
            page.update()
            return

        if not ruta_resuelta.is_dir():
            salida.value = f"La ruta indicada no es una carpeta: {ruta_resuelta}"
            page.update()
            return

        if (
            confirmacion_eliminacion_carpeta_pendiente is None
            or confirmacion_eliminacion_carpeta_pendiente["tipo"] != "carpeta"
            or confirmacion_eliminacion_carpeta_pendiente["ruta"] != ruta_resuelta
        ):
            cancelar_confirmacion_carpeta_eliminacion_pendiente()
            confirmacion_eliminacion_carpeta_pendiente = {
                "tipo": "carpeta",
                "ruta": ruta_resuelta,
                "ruta_visible": ruta_input.value or "",
            }
            salida.value = (
                "Pulsa de nuevo Eliminar carpeta para confirmar: " f"{ruta_resuelta}"
            )
            page.update()
            return

        archivo_activo_en_carpeta = False
        if estado.ruta is not None:
            try:
                estado_ruta_resuelta = estado.ruta.resolve()
                estado_ruta_resuelta.relative_to(ruta_resuelta)
            except ValueError:
                archivo_activo_en_carpeta = False
            else:
                archivo_activo_en_carpeta = True

        try:
            runtime.eliminar_directorio_validado(ruta_resuelta)
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            OSError,
            ValueError,
        ) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return

        cancelar_confirmacion_carpeta_eliminacion_pendiente()

        if archivo_activo_en_carpeta:
            limpiar_archivo_activo()

        reconstruir_arbol()
        salida.value = f"Carpeta eliminada: {ruta_resuelta}"
        actualizar_pagina()

    def archivo_activo_permite_accion_cobra(accion: str) -> bool:
        """Valida que el archivo activo permita una acción propia de Cobra."""

        if estado.ruta is None:
            return True

        if runtime.archivo_permite_accion(estado.ruta, accion):
            return True

        salida.value = "Esta acción solo está disponible para archivos Cobra."
        page.update()
        return False

    ejecutar_runtime_handler = runtime.crear_handler_ejecucion(
        entrada=entrada, salida=salida, selector=selector, activar=activar, page=page
    )
    tokens_runtime_handler = runtime.crear_handler_tokens(
        entrada=entrada, salida=salida, page=page
    )
    ast_runtime_handler = runtime.crear_handler_ast(
        entrada=entrada, salida=salida, page=page
    )
    sugerencias_runtime_handler = runtime.crear_handler_sugerencias(
        entrada=entrada, salida=salida, page=page
    )
    correccion_runtime_handler = runtime.crear_handler_correccion_tipografica(
        entrada=entrada, salida=salida, page=page
    )

    def ejecutar_handler(e):
        if archivo_activo_permite_accion_cobra(runtime.ACCION_EJECUTAR):
            ejecutar_runtime_handler(e)

    def tokens_handler(e):
        if archivo_activo_permite_accion_cobra(runtime.ACCION_TOKENS):
            tokens_runtime_handler(e)

    def ast_handler(e):
        if archivo_activo_permite_accion_cobra(runtime.ACCION_AST):
            ast_runtime_handler(e)

    def sugerencias_handler(e):
        if archivo_activo_permite_accion_cobra(runtime.ACCION_SUGERENCIAS):
            sugerencias_runtime_handler(e)

    def correccion_handler(e):
        if archivo_activo_permite_accion_cobra(runtime.ACCION_CORRECCION):
            correccion_runtime_handler(e)

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
                    runtime.flet_elevated_button(
                        ft, "Cerrar proyecto", on_click=cerrar_proyecto_handler
                    ),
                    runtime.flet_elevated_button(
                        ft, "Eliminar proyecto", on_click=eliminar_proyecto_handler
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
            runtime.flet_elevated_button(
                ft, "Eliminar archivo", on_click=eliminar_archivo_handler
            ),
            runtime.flet_elevated_button(
                ft, "Eliminar carpeta", on_click=eliminar_carpeta_handler
            ),
            runtime.flet_elevated_button(
                ft, "Eliminar proyecto", on_click=eliminar_proyecto_handler
            ),
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
                runtime.flet_text(ft, value="Archivos del proyecto"),
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
