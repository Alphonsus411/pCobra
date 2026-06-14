"""Entorno interactivo para ejecutar código Cobra y explorar tokens y AST."""

from pathlib import Path
from typing import TYPE_CHECKING

from pcobra.gui import runtime

if TYPE_CHECKING:
    import flet as ft


def main(page: "ft.Page"):
    """Interfaz extendida del IDLE con tokens, AST, archivos, árbol y sugerencias."""
    ft = runtime.require_flet()

    estado = runtime.GuiFileState()
    directorio_actual = Path.cwd()

    entrada = runtime.crear_editor_codigo(ft)
    salida = runtime.crear_salida_seleccionable(ft)
    estado_archivo = runtime.flet_text(ft, value="Archivo nuevo (sin guardar)")
    ruta_input = runtime.flet_text_field(ft, label="Ruta", value="", expand=True)
    arbol = runtime.flet_list_view(ft, expand=True, spacing=2, auto_scroll=False)
    lenguajes = list(runtime.gui_target_choices())
    selector = runtime.crear_selector_target(ft, lenguajes=lenguajes)
    activar = runtime.crear_switch_transpilacion(ft, lenguajes=lenguajes)

    def ruta_mostrada() -> str:
        """Devuelve el título específico del IDLE para el archivo activo."""
        ruta = estado.ruta
        nombre = str(ruta) if ruta is not None else "Archivo nuevo (sin guardar)"
        return f"{nombre}{' *' if estado.cambios_sin_guardar else ''}"

    def sincronizar_estado_visual() -> None:
        """Sincroniza controles específicos del IDLE con el estado de archivo."""
        estado_archivo.value = ruta_mostrada()
        ruta_input.value = str(estado.ruta or "")

    def marcar_cambios(_e=None) -> None:
        """Marca cambios sin guardar; comportamiento exclusivo del IDLE."""
        estado.cambios_sin_guardar = (
            runtime.normalizar_codigo(entrada.value) != estado.contenido_cargado
        )
        sincronizar_estado_visual()
        page.update()

    entrada.on_change = marcar_cambios

    def mostrar_error_archivo(exc: Exception) -> None:
        """Muestra errores de archivos en la salida extendida del IDLE."""
        salida.value = runtime.formatear_error(exc)

    def cargar_archivo(ruta: Path) -> None:
        """Carga un archivo Cobra desde el árbol o ruta del IDLE."""
        nonlocal directorio_actual
        try:
            contenido = runtime.leer_archivo_texto(ruta)
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            UnicodeError,
        ) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return
        estado.ruta = ruta.expanduser().resolve()
        estado.contenido_cargado = contenido
        estado.cambios_sin_guardar = False
        directorio_actual = estado.ruta.parent
        entrada.value = contenido
        salida.value = f"Archivo cargado: {estado.ruta}"
        sincronizar_estado_visual()
        reconstruir_arbol()
        page.update()

    def guardar_en(ruta: Path) -> bool:
        """Guarda el editor en una ruta; acción específica del IDLE."""
        try:
            contenido_guardado = runtime.escribir_archivo_texto(ruta, entrada.value)
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
            UnicodeError,
        ) as exc:
            mostrar_error_archivo(exc)
            page.update()
            return False
        estado.ruta = ruta.expanduser().resolve()
        estado.contenido_cargado = contenido_guardado
        estado.cambios_sin_guardar = False
        salida.value = f"Archivo guardado: {estado.ruta}"
        sincronizar_estado_visual()
        reconstruir_arbol()
        page.update()
        return True

    def reconstruir_arbol() -> None:
        """Reconstruye el árbol lateral de archivos Cobra del IDLE."""
        arbol.controls.clear()
        arbol.controls.append(
            runtime.flet_text(ft, value=f"Directorio: {directorio_actual}")
        )
        if directorio_actual.parent != directorio_actual:
            arbol.controls.append(
                runtime.flet_text_button(
                    ft,
                    "📁 ..",
                    on_click=lambda _e: cambiar_directorio(directorio_actual.parent),
                )
            )
        try:
            entradas = runtime.listar_directorio_cobra(directorio_actual)
        except (FileNotFoundError, NotADirectoryError, PermissionError) as exc:
            mostrar_error_archivo(exc)
            entradas = []
        for ruta in entradas:
            if ruta.is_dir():
                arbol.controls.append(
                    runtime.flet_text_button(
                        ft,
                        f"📁 {ruta.name}",
                        on_click=lambda _e, r=ruta: cambiar_directorio(r),
                    )
                )
            else:
                arbol.controls.append(
                    runtime.flet_text_button(
                        ft,
                        f"📄 {ruta.name}",
                        on_click=lambda _e, r=ruta: cargar_archivo(r),
                    )
                )

    def cambiar_directorio(ruta: Path) -> None:
        """Cambia el directorio explorado por el árbol lateral del IDLE."""
        nonlocal directorio_actual
        directorio_actual = ruta.expanduser().resolve()
        reconstruir_arbol()
        page.update()

    def nuevo_handler(_e):
        """Crea un documento nuevo en memoria; acción específica del IDLE."""
        estado.ruta = None
        estado.contenido_cargado = ""
        estado.cambios_sin_guardar = False
        entrada.value = ""
        salida.value = "Archivo nuevo creado en memoria."
        sincronizar_estado_visual()
        page.update()

    def abrir_handler(_e):
        """Abre la ruta escrita en el campo Ruta del IDLE."""
        if not ruta_input.value:
            salida.value = (
                "Indica una ruta para abrir o selecciona un archivo del árbol."
            )
            page.update()
            return
        cargar_archivo(Path(ruta_input.value))

    def guardar_handler(_e):
        """Guarda el archivo activo del IDLE o delega en Guardar como."""
        if estado.ruta is None:
            guardar_como_handler(_e)
            return
        guardar_en(estado.ruta)

    def guardar_como_handler(_e):
        """Guarda el documento del IDLE en la ruta indicada."""
        if not ruta_input.value:
            salida.value = "Indica una ruta de destino en el campo Ruta."
            page.update()
            return
        guardar_en(Path(ruta_input.value))

    def recargar_handler(_e):
        """Recarga desde disco el archivo activo del IDLE."""
        if estado.ruta is None:
            salida.value = "No hay archivo activo que recargar."
            page.update()
            return
        cargar_archivo(estado.ruta)

    ejecutar_handler = runtime.crear_handler_ejecucion(
        entrada=entrada,
        salida=salida,
        selector=selector,
        activar=activar,
        page=page,
    )

    def tokens_handler(_e):
        """Muestra tokens; herramienta extendida exclusiva del IDLE."""
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
        """Muestra el AST; herramienta extendida exclusiva del IDLE."""
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

    def sugerencias_handler(_e):
        """Genera sugerencias estilísticas; herramienta extendida del IDLE."""
        deps = runtime.require_gui_dependencies()
        codigo = runtime.normalizar_codigo(entrada.value)
        try:
            deps["Parser"](deps["Lexer"](codigo).tokenizar()).parsear()
        except Exception as exc:
            error = runtime.formatear_error(
                exc,
                lexer_error_type=deps.get("LexerError"),
                parser_error_type=deps.get("ParserError"),
            )
            salida.value = (
                "Errores léxicos/sintácticos:\n"
                f"- {error}\n\n"
                "Sugerencias estilísticas:\n"
                "- Corrige primero los errores anteriores para solicitar sugerencias."
            )
            page.update()
            return

        try:
            from pcobra.ia.analizador_agix import generar_sugerencias

            sugerencias = generar_sugerencias(codigo)
        except ImportError as exc:
            salida.value = (
                "Errores léxicos/sintácticos:\n"
                "- No se detectaron errores con el Lexer y Parser de Cobra.\n\n"
                "Sugerencias estilísticas:\n"
                f"- No se pudieron generar sugerencias: {exc}. "
                "Instala la dependencia opcional 'agix' para activar esta acción."
            )
        except Exception as exc:
            salida.value = runtime.formatear_error(
                exc,
                lexer_error_type=deps.get("LexerError"),
                parser_error_type=deps.get("ParserError"),
            )
        else:
            if sugerencias:
                sugerencias_legibles = "\n".join(
                    f"- {sugerencia}" for sugerencia in sugerencias
                )
            else:
                sugerencias_legibles = "- No se recibieron sugerencias."
            salida.value = (
                "Errores léxicos/sintácticos:\n"
                "- No se detectaron errores con el Lexer y Parser de Cobra.\n\n"
                "Sugerencias estilísticas:\n"
                f"{sugerencias_legibles}"
            )
        finally:
            page.update()

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
            runtime.flet_elevated_button(
                ft, "Sugerencias", on_click=sugerencias_handler
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
