"""Runtime compartido para las interfaces GUI de Cobra."""

import io
import re
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.ia.analizador_agix import generar_sugerencias


@lru_cache(maxsize=1)
def require_gui_dependencies() -> dict[str, Any]:
    """Importa dependencias de núcleo/transpiladores de forma diferida."""
    try:
        from pcobra.cobra.gui import deps as gui_deps
    except (ImportError, ModuleNotFoundError) as exc:  # pragma: no cover - validado desde CLI
        missing_target, action = _parse_missing_target(exc)
        detail = str(exc) or repr(exc)
        raise RuntimeError(
            "Error de importación GUI en 'pcobra.gui.runtime': "
            f"faltante detectado '{missing_target}'. "
            f"Detalle: {detail}. "
            f"Acción sugerida: {action}"
        ) from exc

    return {
        "Lexer": gui_deps.Lexer,
        "LexerError": gui_deps.LexerError,
        "Parser": gui_deps.Parser,
        "ParserError": gui_deps.ParserError,
        "target_cli_choices": gui_deps.target_cli_choices,
        "OFFICIAL_TARGETS": gui_deps.OFFICIAL_TARGETS,
        "InterpretadorCobra": gui_deps.InterpretadorCobra,
        "TRANSPILERS": gui_deps.get_transpilers(),
    }


def _parse_missing_target(exc: ImportError) -> tuple[str, str]:
    """Detecta el objetivo de importación faltante y sugiere acción."""
    detail = str(exc) or repr(exc)
    if isinstance(exc, ModuleNotFoundError):
        missing_module = getattr(exc, "name", None) or "desconocido"
        return missing_module, _dependency_action(missing_module)

    cannot_import_match = re.search(r"cannot import name '([^']+)' from '([^']+)'", detail)
    if cannot_import_match:
        symbol_name, module_name = cannot_import_match.groups()
        target = f"{module_name}.{symbol_name}"
        return target, _local_import_action(module_name, symbol_name)

    missing_module = getattr(exc, "name", None) or "desconocido"
    return missing_module, _dependency_action(missing_module)


def _dependency_action(missing_module: str) -> str:
    if missing_module.startswith("pcobra."):
        return (
            "corrige el import local y verifica que el módulo exista; "
            "si hace falta reinstala con 'pip install -e .'."
        )
    return f"instala la dependencia que provee '{missing_module}' o ajusta el import local."


def _local_import_action(module_name: str, symbol_name: str) -> str:
    return (
        f"corrige el import local de '{module_name}.{symbol_name}' "
        "o actualiza la dependencia que lo expone."
    )


COBRA_FILE_EXTENSIONS: tuple[str, ...] = (".co", ".cobra")
"""Extensiones Cobra priorizadas para el explorador del IDLE."""


@dataclass(slots=True)
class GuiFileState:
    """Estado mínimo del archivo editado en la GUI."""

    ruta: Path | None = None
    contenido_cargado: str = ""
    cambios_sin_guardar: bool = False


def es_archivo_cobra(path: str | Path) -> bool:
    """Indica si una ruta parece contener código Cobra editable."""

    return Path(path).suffix.lower() in COBRA_FILE_EXTENSIONS


def listar_directorio_cobra(root: str | Path) -> list[Path]:
    """Lista carpetas y archivos Cobra de un directorio, con orden estable."""

    base = Path(root).expanduser()
    entradas = list(base.iterdir())
    visibles = [entry for entry in entradas if entry.is_dir() or es_archivo_cobra(entry)]
    return sorted(visibles, key=lambda entry: (not entry.is_dir(), entry.name.lower()))


def leer_archivo_texto(path: str | Path, *, encoding: str = "utf-8") -> str:
    """Lee un archivo Cobra como texto UTF-8 sin interpretar su contenido."""

    return Path(path).expanduser().read_text(encoding=encoding)


def escribir_archivo_texto(
    path: str | Path, contenido: str | None, *, encoding: str = "utf-8"
) -> str:
    """Escribe exactamente el contenido normalizado del editor y lo devuelve."""

    codigo = normalizar_codigo(contenido)
    destino = Path(path).expanduser()
    destino.write_text(codigo, encoding=encoding)
    return codigo


def require_flet() -> Any:
    """Importa Flet de forma diferida para no romper imports de CLI."""
    try:
        import flet as ft
    except ModuleNotFoundError as exc:  # pragma: no cover - validado desde CLI
        raise RuntimeError("Falta la dependencia 'flet'. Ejecuta: pip install flet.") from exc
    return ft


def _flet_attr(ft: Any, attr_name: str, api_name: str) -> Any:
    """Devuelve una API raíz de Flet o falla con un mensaje homogéneo."""

    attr = getattr(ft, attr_name, None)
    if attr is None:
        raise RuntimeError(f"La versión instalada de 'flet' no expone {api_name}.")
    return attr


def flet_app(target: Any, *args: Any, ft: Any | None = None, **kwargs: Any) -> Any:
    """Lanza ``ft.app`` desde un único adaptador compatible."""

    flet_runtime = ft if ft is not None else require_flet()
    app_factory = _flet_attr(flet_runtime, "app", "app")
    return app_factory(*args, target=target, **kwargs)


def flet_text_field(ft: Any, **kwargs: Any) -> Any:
    """Crea ``ft.TextField`` validando la API desde el runtime central."""

    return _flet_attr(ft, "TextField", "TextField")(**kwargs)


def flet_text(ft: Any, *args: Any, **kwargs: Any) -> Any:
    """Crea ``ft.Text`` validando la API desde el runtime central."""

    return _flet_attr(ft, "Text", "Text")(*args, **kwargs)


def flet_dropdown(ft: Any, **kwargs: Any) -> Any:
    """Crea ``ft.Dropdown`` validando la API desde el runtime central."""

    return _flet_attr(ft, "Dropdown", "Dropdown")(**kwargs)


def flet_switch(ft: Any, **kwargs: Any) -> Any:
    """Crea ``ft.Switch`` validando la API desde el runtime central."""

    return _flet_attr(ft, "Switch", "Switch")(**kwargs)


def flet_elevated_button(ft: Any, *args: Any, **kwargs: Any) -> Any:
    """Crea ``ft.ElevatedButton`` validando la API desde el runtime central."""

    return _flet_attr(ft, "ElevatedButton", "ElevatedButton")(*args, **kwargs)


def flet_text_button(ft: Any, *args: Any, **kwargs: Any) -> Any:
    """Crea ``ft.TextButton`` validando la API desde el runtime central."""

    return _flet_attr(ft, "TextButton", "TextButton")(*args, **kwargs)


def flet_row(ft: Any, *args: Any, **kwargs: Any) -> Any:
    """Crea ``ft.Row`` validando la API desde el runtime central."""

    return _flet_attr(ft, "Row", "Row")(*args, **kwargs)


def flet_column(ft: Any, *args: Any, **kwargs: Any) -> Any:
    """Crea ``ft.Column`` validando la API desde el runtime central."""

    return _flet_attr(ft, "Column", "Column")(*args, **kwargs)


def flet_container(ft: Any, *args: Any, **kwargs: Any) -> Any:
    """Crea ``ft.Container`` validando la API desde el runtime central."""

    return _flet_attr(ft, "Container", "Container")(*args, **kwargs)


def flet_list_view(ft: Any, *args: Any, **kwargs: Any) -> Any:
    """Crea ``ft.ListView`` validando la API desde el runtime central."""

    return _flet_attr(ft, "ListView", "ListView")(*args, **kwargs)


def flet_dropdown_option(ft: Any, value: str) -> Any:
    """Crea una opción de Dropdown compatible con versiones recientes de Flet."""

    option_factory = getattr(ft, "Option", None)
    if option_factory is not None:
        return option_factory(value)

    dropdown_module = getattr(ft, "dropdown", None)
    option_factory = getattr(dropdown_module, "Option", None)
    if option_factory is None:
        raise RuntimeError(
            "La versión instalada de 'flet' no expone Option ni dropdown.Option."
        )
    return option_factory(value)


def crear_editor_codigo(ft: Any, **kwargs: Any) -> Any:
    """Crea el editor de código compartido por la app mínima y el IDLE."""

    opciones = {"multiline": True, "expand": True}
    opciones.update(kwargs)
    return flet_text_field(ft, **opciones)


def crear_salida_seleccionable(ft: Any, **kwargs: Any) -> Any:
    """Crea la salida seleccionable compartida por la app mínima y el IDLE."""

    opciones = {"value": "", "selectable": True}
    opciones.update(kwargs)
    return flet_text(ft, **opciones)


def crear_arbol_directorios(ft: Any, *, on_click: Any, root_path: Path | None = None) -> Any:
    """Crea un componente de árbol de directorios para la GUI."""
    if root_path is None:
        root_path = Path(".").resolve()

    def _crear_nodo_directorio(path: Path) -> Any:
        if path.is_dir():
            children = []
            for entry in listar_directorio_cobra(path):
                children.append(_crear_nodo_directorio(entry))
            return ft.ExpansionTile(
                title=ft.Text(path.name),
                leading=ft.Icon(ft.icons.FOLDER),
                controls=children,
            )
        else:
            return ft.ListTile(
                title=ft.Text(path.name),
                leading=ft.Icon(ft.icons.INSERT_DRIVE_FILE),
                data=str(path),
                on_click=on_click,
            )

    elementos_arbol = []
    for entrada in listar_directorio_cobra(root_path):
        elementos_arbol.append(_crear_nodo_directorio(entrada))

    return ft.Column(elementos_arbol, scroll=ft.ScrollMode.ALWAYS)


def crear_selector_target(ft: Any, *, lenguajes: list[str] | None = None) -> Any:
    """Crea el selector de target compartido para transpilación en GUI."""

    targets = list(gui_target_choices()) if lenguajes is None else lenguajes
    selector = flet_dropdown(
        ft, options=[flet_dropdown_option(ft, lang) for lang in targets]
    )
    if targets:
        selector.value = targets[0]
    return selector


def crear_switch_transpilacion(ft: Any, *, lenguajes: list[str] | None = None) -> Any:
    """Crea el switch compartido que alterna ejecución y transpilación."""

    targets = list(gui_target_choices()) if lenguajes is None else lenguajes
    return flet_switch(ft, label="Transpilar", disabled=not targets)


def ejecutar_o_transpilar(codigo: str, *, transpilacion_activa: bool, target: str) -> str:
    """Ejecuta o transpila código Cobra; lógica compartida por ambas GUIs."""

    deps = require_gui_dependencies()
    if transpilacion_activa and target not in deps["TRANSPILERS"]:
        return "Selecciona un lenguaje destino para transpilar"
    if transpilacion_activa:
        return transpilar_codigo(codigo, target)
    return ejecutar_codigo(codigo)


def crear_handler_ejecucion(
    *,
    entrada: Any,
    salida: Any,
    selector: Any,
    activar: Any,
    page: Any,
) -> Any:
    """Crea el handler compartido de ejecutar/transpilar para app mínima e IDLE."""

    def ejecutar_handler(_e: Any) -> None:
        deps = require_gui_dependencies()
        codigo = normalizar_codigo(entrada.value)
        try:
            salida.value = ejecutar_o_transpilar(
                codigo,
                transpilacion_activa=bool(activar.value),
                target=str(selector.value or ""),
            )
        except Exception as exc:
            salida.value = formatear_error(
                exc,
                lexer_error_type=deps.get("LexerError"),
                parser_error_type=deps.get("ParserError"),
            )
        finally:
            page.update()

    return ejecutar_handler


def _guardar_archivo(page: Any, entrada: Any, estado_archivo: GuiFileState, ruta: Path) -> None:
    """Guarda el contenido del editor en la ruta especificada."""
    try:
        contenido_guardado = escribir_archivo_texto(ruta, entrada.value)
        estado_archivo.ruta = ruta
        estado_archivo.contenido_cargado = contenido_guardado
        estado_archivo.cambios_sin_guardar = False
        page.snack_bar.open = True
        page.snack_bar.content = flet_text(
            require_flet(), f"Archivo guardado en {ruta}"
        )
    except Exception as exc:
        page.snack_bar.open = True
        page.snack_bar.content = flet_text(
            require_flet(), f"Error al guardar: {exc}"
        )
    finally:
        page.update()


def crear_handler_guardar(
    *,
    entrada: Any,
    estado_archivo: GuiFileState,
    page: Any,
) -> Any:
    """Crea el handler para guardar el archivo actual."""

    def guardar_handler(_e: Any) -> None:
        if estado_archivo.ruta:
            _guardar_archivo(page, entrada, estado_archivo, estado_archivo.ruta)
        else:
            # Si no hay ruta, invocar "Guardar como"
            crear_handler_guardar_como(entrada=entrada, estado_archivo=estado_archivo, page=page)(_e)

    return guardar_handler


def crear_handler_guardar_como(
    *,
    entrada: Any,
    estado_archivo: GuiFileState,
    page: Any,
) -> Any:
    """Crea el handler para guardar el archivo con un nuevo nombre/ruta."""

    def guardar_como_handler(_e: Any) -> None:
        flet_runtime = require_flet()

        def on_file_dialog_result(e: Any) -> None:
            if e.path:
                _guardar_archivo(page, entrada, estado_archivo, Path(e.path))

        file_picker = _flet_attr(flet_runtime, "FilePicker", "FilePicker")(
            on_result=on_file_dialog_result
        )
        page.overlay.append(file_picker)
        page.update()
        file_picker.save_file(
            dialog_title="Guardar archivo Cobra",
            file_name="nuevo_archivo.cobra",
            allowed_extensions=["cobra", "co"],
        )

    return guardar_como_handler


def crear_handler_sugerencias_agix(
    *,
    entrada: Any,
    salida: Any,
    page: Any,
) -> Any:
    """Crea el handler para generar sugerencias de código con Agix."""

    def sugerencias_agix_handler(_e: Any) -> None:
        deps = require_gui_dependencies()
        codigo = normalizar_codigo(entrada.value)
        try:
            # ``generar_sugerencias`` centraliza la validación con Lexer/Parser
            # y evita depender de modelos internos de ``agix.models.*``.
            sugerencias = generar_sugerencias(codigo)
        except ImportError as exc:
            salida.value = (
                "Agix no está instalado o no está disponible. "
                "Instálalo con 'pip install agix' para usar esta función. "
                f"Detalle: {exc}"
            )
        except Exception as exc:
            salida.value = formatear_error(
                exc,
                lexer_error_type=deps.get("LexerError"),
                parser_error_type=deps.get("ParserError"),
            )
        else:
            if sugerencias:
                salida.value = "Sugerencias de Agix:\n" + "\n".join(
                    f"- {sugerencia}" for sugerencia in sugerencias
                )
            else:
                salida.value = "Agix no encontró sugerencias para el código actual."
        finally:
            page.update()

    return sugerencias_agix_handler


def normalizar_codigo(codigo: str | None) -> str:
    """Normaliza la entrada para evitar valores ``None``."""
    return codigo or ""


def ejecutar_codigo(codigo: str) -> str:
    """Ejecuta código Cobra y captura la salida impresa."""
    deps = require_gui_dependencies()
    buffer = io.StringIO()
    with redirect_stdout(buffer), redirect_stderr(buffer):
        tokens = deps["Lexer"](codigo).tokenizar()
        ast = deps["Parser"](tokens).parsear()
        deps["InterpretadorCobra"]().ejecutar_ast(ast)
    return buffer.getvalue()


def transpilar_codigo(codigo: str, lang: str) -> str:
    """Transpila código Cobra al lenguaje especificado."""
    deps = require_gui_dependencies()
    tokens = deps["Lexer"](codigo).tokenizar()
    ast = deps["Parser"](tokens).parsear()
    transp = deps["TRANSPILERS"][lang]()
    return transp.generate_code(ast)


def mostrar_tokens(codigo: str) -> str:
    """Tokeniza código Cobra y devuelve una representación por línea."""
    deps = require_gui_dependencies()
    tokens = deps["Lexer"](codigo).tokenizar()
    return "\n".join(str(token) for token in tokens)


def mostrar_ast(codigo: str) -> str:
    """Parsea código Cobra y devuelve una representación serializada del AST."""
    deps = require_gui_dependencies()
    tokens = deps["Lexer"](codigo).tokenizar()
    ast = deps["Parser"](tokens).parsear()
    return str(ast)


def formatear_error(
    exc: Exception,
    *,
    lexer_error_type: type[BaseException] | None = None,
    parser_error_type: type[BaseException] | None = None,
) -> str:
    """Convierte excepciones en mensajes legibles para la GUI.

    ``lexer_error_type`` y ``parser_error_type`` se inyectan desde una capa ya
    inicializada (GUI handlers) para evitar imports/reloads en esta ruta de
    manejo de errores.
    """
    if lexer_error_type is not None and isinstance(exc, lexer_error_type):
        linea = getattr(exc, "linea", "?")
        columna = getattr(exc, "columna", "?")
        return f"Error léxico (línea {linea}, columna {columna}): {exc}"
    if parser_error_type is not None and isinstance(exc, parser_error_type):
        return f"Error de sintaxis: {exc}"
    return f"Error de ejecución: {exc}"


def gui_target_choices() -> tuple[str, ...]:
    """Devuelve targets públicos canónicos visibles en GUI preservando el orden oficial."""
    deps = require_gui_dependencies()
    official_targets = tuple(deps["OFFICIAL_TARGETS"])
    if official_targets != PUBLIC_BACKENDS:
        raise RuntimeError(
            "Contrato público inválido en GUI: OFFICIAL_TARGETS debe coincidir con PUBLIC_BACKENDS. "
            f"official={official_targets}; public={PUBLIC_BACKENDS}"
        )
    return deps["target_cli_choices"](
        set(PUBLIC_BACKENDS) & set(deps["TRANSPILERS"])
    )
