"""Runtime compartido para las interfaces GUI de Cobra."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
from functools import lru_cache
from typing import Any

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS


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
