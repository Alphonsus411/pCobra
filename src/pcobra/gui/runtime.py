"""Runtime compartido para las interfaces GUI de Cobra."""

import io
import importlib.util
import os
import re
import shutil
import warnings
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.corelibs.archivo import _resolver_ruta as resolver_ruta_sandbox


@lru_cache(maxsize=1)
def require_gui_dependencies() -> dict[str, Any]:
    """Importa dependencias de núcleo/transpiladores de forma diferida."""
    try:
        from pcobra.cobra.gui import deps as gui_deps
    except (
        ImportError,
        ModuleNotFoundError,
    ) as exc:  # pragma: no cover - validado desde CLI
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

    cannot_import_match = re.search(
        r"cannot import name '([^']+)' from '([^']+)'", detail
    )
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


TIPO_ARCHIVO_COBRA = "cobra"
TIPO_ARCHIVO_MARKDOWN = "markdown"
TIPO_ARCHIVO_TEXTO = "texto"
TIPO_ARCHIVO_CONFIG = "config"
TIPO_ARCHIVO_DOCKER = "docker"
TIPO_ARCHIVO_IGNORE = "ignore"
TIPO_ARCHIVO_ENV_EXAMPLE = "env_example"
TIPO_ARCHIVO_DESCONOCIDO = "desconocido"

ACCION_EDITAR = "editar"
ACCION_GUARDAR = "guardar"
ACCION_RECARGAR = "recargar"
ACCION_BORRAR = "borrar"
ACCION_EJECUTAR = "ejecutar"
ACCION_TOKENS = "tokens"
ACCION_AST = "ast"
ACCION_SUGERENCIAS = "sugerencias"
ACCION_CORRECCION = "correccion"

ACCIONES_ARCHIVO_BASE: frozenset[str] = frozenset(
    {ACCION_EDITAR, ACCION_GUARDAR, ACCION_RECARGAR, ACCION_BORRAR}
)
"""Acciones comunes para archivos manipulables desde la GUI."""

ACCIONES_ARCHIVO_COBRA: frozenset[str] = ACCIONES_ARCHIVO_BASE | frozenset(
    {
        ACCION_EJECUTAR,
        ACCION_TOKENS,
        ACCION_AST,
        ACCION_SUGERENCIAS,
        ACCION_CORRECCION,
    }
)
"""Acciones disponibles para archivos Cobra."""

COBRA_FILE_EXTENSIONS: tuple[str, ...] = (".cobra", ".co")
"""Extensiones Cobra aceptadas y priorizadas para el explorador del IDLE."""

MARKDOWN_FILE_EXTENSIONS: frozenset[str] = frozenset({".md", ".markdown"})
TEXT_FILE_EXTENSIONS: frozenset[str] = frozenset({".txt"})
CONFIG_FILE_EXTENSIONS: frozenset[str] = frozenset(
    {".json", ".yml", ".yaml", ".toml"}
)
IGNORE_FILE_NAMES: frozenset[str] = frozenset({".gitignore", ".dockerignore"})
ENV_EXAMPLE_FILE_NAMES: frozenset[str] = frozenset({".env.example"})
"""Nombres especiales de archivos de entorno de ejemplo."""

CAPACIDADES_POR_TIPO: dict[str, frozenset[str]] = {
    TIPO_ARCHIVO_COBRA: ACCIONES_ARCHIVO_COBRA,
    TIPO_ARCHIVO_MARKDOWN: ACCIONES_ARCHIVO_BASE,
    TIPO_ARCHIVO_TEXTO: ACCIONES_ARCHIVO_BASE,
    TIPO_ARCHIVO_CONFIG: ACCIONES_ARCHIVO_BASE,
    TIPO_ARCHIVO_DOCKER: ACCIONES_ARCHIVO_BASE,
    TIPO_ARCHIVO_IGNORE: ACCIONES_ARCHIVO_BASE,
    TIPO_ARCHIVO_ENV_EXAMPLE: ACCIONES_ARCHIVO_BASE,
    TIPO_ARCHIVO_DESCONOCIDO: ACCIONES_ARCHIVO_BASE,
}
"""Acciones permitidas por tipo de archivo detectado."""

MOSTRAR_DESCONOCIDOS_COMO_TEXTO_IDLE = False
"""Bandera interna para exponer archivos desconocidos como texto plano.

El valor por defecto mantiene visible solo lo que la GUI clasifica como Cobra o
texto/configuración auxiliar soportado por ``detectar_tipo_archivo()``. Puede
activarse desde código o una configuración futura si el equipo decide permitir
abrir archivos desconocidos como texto plano desde el árbol del IDLE.
"""

SUGERENCIAS_BUTTON_TEXT = "Sugerencias del Libro"
"""Etiqueta homogénea para la acción de sugerencias trazables en las GUIs."""

CORRECCION_BUTTON_TEXT = "Corrección"
"""Etiqueta para solicitar un reporte de corrección tipográfica sin modificar el editor."""

CANONICAL_SUGGESTION_ENGINE = "agix"
"""Motor opcional canónico para sugerencias de Cobra."""


def resolver_workspace_root_idle() -> Path:
    """Resuelve y crea la raíz de trabajo inicial del IDLE sin usar ``Path.cwd()``."""

    configured_root = os.environ.get("COBRA_PROJECTS_DIR")
    if configured_root:
        workspace_root = Path(configured_root).expanduser().resolve()
    else:
        workspace_root = (Path.home() / "CobraProjects").expanduser().resolve()

    workspace_root.mkdir(parents=True, exist_ok=True)
    return workspace_root


def resolver_repo_root_gui() -> Path:
    """Resuelve la raíz del repositorio de Cobra relativa a este módulo GUI."""

    return Path(__file__).resolve().parents[3]


def _es_misma_ruta(candidata: Path, prohibida: Path) -> bool:
    """Compara rutas canónicas usando ``Path.relative_to()`` de forma portable."""

    try:
        relativa = candidata.relative_to(prohibida)
    except ValueError:
        return False
    return relativa == Path(".")


def validar_project_root_idle(project_root: str | Path) -> Path:
    """Valida que la raíz de proyecto del IDLE no sea una ruta interna del repo.

    El IDLE debe abrir proyectos de usuario, no la raíz del repositorio ni las
    carpetas de código fuente de la propia aplicación. La comparación usa rutas
    resueltas y ``Path.relative_to()`` para conservar compatibilidad con Windows.
    """

    candidata = Path(project_root).expanduser().resolve()
    repo_root = resolver_repo_root_gui()
    rutas_prohibidas = {
        repo_root: "la raíz del repositorio",
        repo_root / "src": "src/",
        repo_root / "src" / "pcobra": "src/pcobra/",
        repo_root / "src" / "pcobra" / "gui": "src/pcobra/gui/",
    }

    for ruta_prohibida, descripcion in rutas_prohibidas.items():
        ruta_prohibida_resuelta = ruta_prohibida.resolve()
        if _es_misma_ruta(candidata, ruta_prohibida_resuelta):
            raise ValueError(
                "No se puede abrir como proyecto del IDLE "
                f"{descripcion}: {ruta_prohibida_resuelta}. "
                "Elige una carpeta de proyecto fuera del código fuente de Cobra."
            )

    return candidata


@dataclass(frozen=True, slots=True)
class MotorIASugerencias:
    """Resultado liviano de disponibilidad del motor IA para sugerencias."""

    disponible: bool
    nombre: str = CANONICAL_SUGGESTION_ENGINE
    detalle: str = ""

    @property
    def tooltip(self) -> str:
        """Mensaje breve para explicar el estado en la GUI."""

        if self.disponible:
            return (
                "Motor IA opcional disponible. "
                "Las sugerencias validarán primero el código Cobra."
            )
        return self.detalle or (
            "Sugerencias deshabilitadas: instala la dependencia opcional "
            f"de sugerencias {CANONICAL_SUGGESTION_ENGINE!r} para activar esta acción."
        )


@dataclass(slots=True)
class GuiFileState:
    """Estado mínimo del archivo editado en la GUI."""

    ruta: Path | None = None
    contenido_cargado: str = ""
    cambios_sin_guardar: bool = False


@lru_cache(maxsize=1)
def detectar_motor_ia_sugerencias() -> MotorIASugerencias:
    """Detecta de forma liviana si el motor IA opcional está instalado.

    La comprobación usa metadatos de importación y no importa la dependencia
    opcional ni la fachada de sugerencias, evitando cargar dependencias pesadas
    al abrir la GUI.
    """

    try:
        spec = importlib.util.find_spec(CANONICAL_SUGGESTION_ENGINE)
    except (ImportError, ModuleNotFoundError, ValueError) as exc:
        return MotorIASugerencias(
            disponible=False,
            detalle=(
                "Sugerencias deshabilitadas: no se pudo comprobar la "
                f"dependencia opcional {CANONICAL_SUGGESTION_ENGINE!r} ({exc})."
            ),
        )

    if spec is None:
        return MotorIASugerencias(
            disponible=False,
            detalle=(
                "Sugerencias deshabilitadas: instala la dependencia opcional "
                f"{CANONICAL_SUGGESTION_ENGINE!r} para activar esta acción."
            ),
        )
    return MotorIASugerencias(disponible=True)


def generar_sugerencias(codigo: str) -> list[str]:
    """Importa bajo demanda la fachada IA y genera sugerencias."""

    from pcobra.ia.analizador_sugerencias import generar_sugerencias as _generar

    return _generar(codigo)


def detectar_tipo_archivo(path: str | Path) -> str:
    """Clasifica una ruta según los tipos de archivo conocidos por la GUI."""

    ruta = Path(path)
    nombre = ruta.name
    nombre_lower = nombre.lower()
    extension = ruta.suffix.lower()

    if extension in COBRA_FILE_EXTENSIONS:
        return TIPO_ARCHIVO_COBRA
    if extension in MARKDOWN_FILE_EXTENSIONS:
        return TIPO_ARCHIVO_MARKDOWN
    if extension in TEXT_FILE_EXTENSIONS:
        return TIPO_ARCHIVO_TEXTO
    if extension in CONFIG_FILE_EXTENSIONS:
        return TIPO_ARCHIVO_CONFIG
    if nombre == "Dockerfile" or nombre.startswith("Dockerfile."):
        return TIPO_ARCHIVO_DOCKER
    if nombre_lower in IGNORE_FILE_NAMES:
        return TIPO_ARCHIVO_IGNORE
    if nombre_lower in ENV_EXAMPLE_FILE_NAMES:
        return TIPO_ARCHIVO_ENV_EXAMPLE
    return TIPO_ARCHIVO_DESCONOCIDO


def obtener_capacidades_archivo(path: str | Path) -> frozenset[str]:
    """Devuelve las acciones permitidas para el tipo detectado de una ruta."""

    tipo_archivo = detectar_tipo_archivo(path)
    return CAPACIDADES_POR_TIPO.get(tipo_archivo, ACCIONES_ARCHIVO_BASE)


def archivo_permite_accion(path: str | Path, accion: str) -> bool:
    """Indica si una ruta permite ejecutar una acción concreta en la GUI."""

    return accion in obtener_capacidades_archivo(path)


def es_archivo_cobra(path: str | Path) -> bool:
    """Indica si una ruta parece contener código Cobra editable."""

    return detectar_tipo_archivo(path) == TIPO_ARCHIVO_COBRA


def resolver_ruta_archivo_en_project_root(
    ruta: str | Path, project_root: str | Path
) -> Path:
    """Resuelve una ruta de archivo Cobra dentro de la raíz del proyecto IDLE.

    Las rutas relativas se interpretan desde ``project_root`` y las absolutas
    se aceptan únicamente si su ruta canónica queda dentro de esa raíz. La
    resolución con ``Path.resolve()`` y la validación con ``Path.relative_to()``
    bloquean escapes mediante ``..`` y enlaces simbólicos externos.
    """

    raiz = Path(project_root).expanduser().resolve()
    if raiz.exists() and not raiz.is_dir():
        raise NotADirectoryError(f"La raíz del proyecto debe ser un directorio: {raiz}")

    ruta_expandida = Path(ruta).expanduser()
    ruta_con_extension = (
        ruta_expandida.with_suffix(".cobra")
        if not ruta_expandida.suffix
        else ruta_expandida
    )
    if ruta_con_extension.suffix.lower() not in COBRA_FILE_EXTENSIONS:
        raise ValueError("El archivo debe usar la extensión .cobra o .co.")

    candidata_original = (
        ruta_expandida if ruta_expandida.is_absolute() else raiz / ruta_expandida
    ).resolve()
    if candidata_original.exists() and candidata_original.is_dir():
        raise NotADirectoryError(
            "La ruta indicada corresponde a un directorio; indica un archivo Cobra."
        )

    candidata = (
        ruta_con_extension
        if ruta_con_extension.is_absolute()
        else raiz / ruta_con_extension
    )
    ruta_resuelta = candidata.resolve()

    try:
        ruta_resuelta.relative_to(raiz)
    except ValueError as exc:
        raise ValueError(
            f"La ruta del archivo debe estar dentro de la raíz del proyecto: {raiz}"
        ) from exc

    if ruta_resuelta.exists() and ruta_resuelta.is_dir():
        raise NotADirectoryError(
            "La ruta indicada corresponde a un directorio; indica un archivo Cobra."
        )

    return ruta_resuelta


def resolver_ruta_texto_en_project_root(
    ruta: str | Path, project_root: str | Path
) -> Path:
    """Resuelve una ruta de archivo de texto dentro de ``project_root``.

    Las rutas relativas se interpretan desde ``project_root``. Las rutas
    absolutas se aceptan solo si su ruta canónica queda dentro de esa raíz.
    ``Path.resolve()`` junto con ``Path.relative_to()`` bloquea escapes con
    ``..`` y enlaces simbólicos externos. Este helper no añade extensiones ni
    exige que el archivo sea Cobra.
    """

    raiz = Path(project_root).expanduser().resolve()
    if raiz.exists() and not raiz.is_dir():
        raise NotADirectoryError(f"La raíz del proyecto debe ser un directorio: {raiz}")

    ruta_expandida = Path(ruta).expanduser()
    candidata = (
        ruta_expandida if ruta_expandida.is_absolute() else raiz / ruta_expandida
    )
    ruta_resuelta = candidata.resolve()

    try:
        ruta_resuelta.relative_to(raiz)
    except ValueError as exc:
        raise ValueError(
            f"La ruta del archivo debe estar dentro de la raíz del proyecto: {raiz}"
        ) from exc

    if ruta_resuelta.exists() and ruta_resuelta.is_dir():
        raise NotADirectoryError(
            "La ruta indicada corresponde a un directorio; "
            "indica un archivo de texto del proyecto."
        )

    return ruta_resuelta


TIPOS_ARCHIVO_TEXTO_IDLE: frozenset[str] = frozenset(CAPACIDADES_POR_TIPO) - frozenset(
    {TIPO_ARCHIVO_DESCONOCIDO}
)
"""Tipos de archivo no directorio visibles y abribles como texto en el IDLE."""


def listar_directorio_idle(
    root: str | Path,
    *,
    incluir_desconocidos: bool = MOSTRAR_DESCONOCIDOS_COMO_TEXTO_IDLE,
) -> list[Path]:
    """Lista carpetas y archivos visibles del IDLE, con orden estable.

    La política general muestra siempre directorios, archivos Cobra y archivos
    auxiliares de texto/configuración clasificados por ``detectar_tipo_archivo()``
    (por ejemplo Markdown, TXT, JSON/YAML/TOML, Dockerfile, ignore y
    ``.env.example``). ``incluir_desconocidos`` permite exponer archivos no
    clasificados si se decide abrirlos como texto plano.
    """

    base = Path(root).expanduser()
    entradas = list(base.iterdir())
    visibles = []
    for entry in entradas:
        if entry.is_dir():
            visibles.append(entry)
            continue
        tipo_archivo = detectar_tipo_archivo(entry)
        if tipo_archivo in TIPOS_ARCHIVO_TEXTO_IDLE or (
            incluir_desconocidos and tipo_archivo == TIPO_ARCHIVO_DESCONOCIDO
        ):
            visibles.append(entry)

    return sorted(visibles, key=lambda entry: (not entry.is_dir(), entry.name.lower()))


def listar_directorio_cobra(
    root: str | Path,
    *,
    mostrar_todos: bool = MOSTRAR_DESCONOCIDOS_COMO_TEXTO_IDLE,
) -> list[Path]:
    """Lista entradas visibles del IDLE usando la política general actual.

    Legado: se conserva por compatibilidad con integraciones que aún llaman al
    helper histórico centrado en Cobra. Delegue nuevo código en
    ``listar_directorio_idle()``. El parámetro ``mostrar_todos`` se conserva como
    alias compatible para incluir archivos desconocidos como texto plano.
    """

    return listar_directorio_idle(root, incluir_desconocidos=mostrar_todos)


def normalizar_ruta_archivo_gui(path: str | Path) -> Path:
    """Normaliza rutas de la GUI según el sandbox Cobra compartido."""

    return resolver_ruta_sandbox(path, permitir_absoluta_dentro_base=True)


def leer_archivo_texto(path: str | Path, *, encoding: str = "utf-8") -> str:
    """Lee un archivo Cobra como texto UTF-8 dentro del sandbox configurado."""

    return normalizar_ruta_archivo_gui(path).read_text(encoding=encoding)


def escribir_archivo_texto(
    path: str | Path, contenido: str | None, *, encoding: str = "utf-8"
) -> str:
    """Escribe una sola vez el contenido normalizado del editor y lo devuelve."""

    codigo = normalizar_codigo(contenido)
    destino = normalizar_ruta_archivo_gui(path)
    destino.write_text(codigo, encoding=encoding)
    return codigo


def crear_titulo_archivo(estado: GuiFileState) -> str:
    """Devuelve la etiqueta común del archivo activo en la GUI."""

    nombre = (
        str(estado.ruta) if estado.ruta is not None else "Archivo nuevo (sin guardar)"
    )
    return f"{nombre}{' *' if estado.cambios_sin_guardar else ''}"


def marcar_cambios_editor(estado: GuiFileState, contenido: str | None) -> bool:
    """Actualiza el estado sucio comparando editor y contenido cargado."""

    estado.cambios_sin_guardar = (
        normalizar_codigo(contenido) != estado.contenido_cargado
    )
    return estado.cambios_sin_guardar


def nuevo_archivo(estado: GuiFileState) -> str:
    """Reinicia el estado de archivo y devuelve contenido vacío para el editor."""

    estado.ruta = None
    estado.contenido_cargado = ""
    estado.cambios_sin_guardar = False
    return ""


def cargar_archivo_en_estado(ruta: str | Path, estado: GuiFileState) -> str:
    """Carga un archivo de texto, actualiza estado y devuelve su contenido."""

    ruta_resuelta = normalizar_ruta_archivo_gui(ruta)
    contenido = leer_archivo_texto(ruta_resuelta)
    estado.ruta = ruta_resuelta
    estado.contenido_cargado = contenido
    estado.cambios_sin_guardar = False
    return contenido


def guardar_archivo_en_estado(
    ruta: str | Path, contenido: str | None, estado: GuiFileState
) -> str:
    """Guarda contenido del editor, actualiza estado y devuelve el texto guardado."""

    ruta_resuelta = normalizar_ruta_archivo_gui(ruta)
    contenido_guardado = escribir_archivo_texto(ruta_resuelta, contenido)
    estado.ruta = ruta_resuelta
    estado.contenido_cargado = contenido_guardado
    estado.cambios_sin_guardar = False
    return contenido_guardado


def construir_entradas_directorio(
    directorio: str | Path,
) -> tuple[Path | None, list[tuple[str, Path]]]:
    """Devuelve padre opcional y entradas visibles para renderizar árboles GUI."""

    actual = Path(directorio).expanduser().resolve()
    padre = actual.parent if actual.parent != actual else None
    entradas = [
        ("dir" if ruta.is_dir() else "file", ruta)
        for ruta in listar_directorio_idle(actual)
    ]
    return padre, entradas


def crear_archivo_nuevo_en_editor(estado: GuiFileState) -> tuple[str, str]:
    """Prepara un archivo nuevo y devuelve contenido/mensaje para la GUI."""

    return nuevo_archivo(estado), "Archivo nuevo creado en memoria."


def abrir_archivo_desde_ruta(ruta: str | Path, estado: GuiFileState) -> tuple[str, str]:
    """Abre una ruta de archivo, actualiza estado y devuelve contenido/mensaje."""

    contenido = cargar_archivo_en_estado(ruta, estado)
    return contenido, f"Archivo cargado: {estado.ruta}"


def guardar_archivo_activo(
    contenido: str | None, estado: GuiFileState
) -> tuple[str, str]:
    """Guarda el archivo activo y devuelve contenido normalizado/mensaje."""

    if estado.ruta is None:
        raise ValueError("No hay archivo activo que guardar.")
    contenido_guardado = guardar_archivo_en_estado(estado.ruta, contenido, estado)
    return contenido_guardado, f"Archivo guardado: {estado.ruta}"


def guardar_archivo_como(
    ruta: str | Path, contenido: str | None, estado: GuiFileState
) -> tuple[str, str]:
    """Guarda el editor en una ruta nueva y devuelve contenido/mensaje."""

    contenido_guardado = guardar_archivo_en_estado(ruta, contenido, estado)
    return contenido_guardado, f"Archivo guardado: {estado.ruta}"


def escribir_archivo_texto_validado(
    path: str | Path, contenido: str | None, *, encoding: str = "utf-8"
) -> str:
    """Escribe en una ruta ya validada por el IDLE principal.

    Esta función no revalida contra el sandbox global porque el flujo del IDLE
    principal ya validó la ruta contra project_root mediante
    resolver_ruta_texto_en_project_root().
    """

    destino = Path(path).expanduser().resolve()
    if destino.exists() and destino.is_dir():
        raise NotADirectoryError(
            "La ruta indicada corresponde a un directorio; indica un archivo de texto del proyecto."
        )

    destino.parent.mkdir(parents=True, exist_ok=True)
    codigo = normalizar_codigo(contenido)
    destino.write_text(codigo, encoding=encoding)
    return codigo


def guardar_archivo_como_validado(
    ruta: str | Path, contenido: str | None, estado: GuiFileState
) -> tuple[str, str]:
    """Guarda un archivo cuya ruta ya fue validada contra project_root."""

    destino = Path(ruta).expanduser().resolve()
    codigo = escribir_archivo_texto_validado(destino, contenido)
    estado.ruta = destino
    estado.contenido_cargado = codigo
    estado.cambios_sin_guardar = False
    return codigo, f"Archivo guardado: {destino}"


def guardar_archivo_activo_validado(
    contenido: str | None, estado: GuiFileState
) -> tuple[str, str]:
    """Guarda el archivo activo cuya ruta ya fue validada contra project_root."""

    if estado.ruta is None:
        raise ValueError("No hay archivo activo que guardar.")

    destino = Path(estado.ruta).expanduser().resolve()
    codigo = escribir_archivo_texto_validado(destino, contenido)
    estado.ruta = destino
    estado.contenido_cargado = codigo
    estado.cambios_sin_guardar = False
    return codigo, f"Archivo guardado: {destino}"


def eliminar_archivo_validado(ruta: Path) -> None:
    """Elimina un archivo cuya ruta ya fue validada por el IDLE principal."""

    destino = Path(ruta).resolve()
    if not destino.exists():
        raise FileNotFoundError(
            f"No existe el archivo que se quiere eliminar: {destino}"
        )
    if not destino.is_file():
        raise ValueError(f"La ruta indicada no es un archivo: {destino}")
    destino.unlink()


def eliminar_directorio_validado(ruta: Path) -> None:
    """Elimina un directorio cuya ruta ya fue validada por el IDLE principal."""

    destino = Path(ruta).resolve()
    if not destino.exists():
        raise FileNotFoundError(
            f"No existe el directorio que se quiere eliminar: {destino}"
        )
    if not destino.is_dir():
        raise NotADirectoryError(f"La ruta indicada no es un directorio: {destino}")
    shutil.rmtree(destino)


def eliminar_proyecto_validado(project_root: Path, workspace_root: Path) -> None:
    """Elimina un proyecto cuya raíz ya fue validada por el IDLE principal."""

    proyecto = Path(project_root).resolve()
    workspace = Path(workspace_root).resolve()
    if proyecto == workspace:
        raise ValueError("No se puede eliminar la raíz completa del workspace.")
    if proyecto.parent != workspace:
        raise ValueError(
            "La raíz del proyecto debe ser hija directa de la raíz del workspace."
        )
    if not proyecto.exists():
        raise FileNotFoundError(
            f"No existe el proyecto que se quiere eliminar: {proyecto}"
        )
    if not proyecto.is_dir():
        raise NotADirectoryError(
            f"La ruta del proyecto no es un directorio: {proyecto}"
        )
    shutil.rmtree(proyecto)


def leer_archivo_texto_validado(
    path: str | Path, *, encoding: str = "utf-8"
) -> str:
    """Lee una ruta ya validada por el IDLE principal."""

    origen = Path(path).expanduser().resolve()
    if origen.exists() and origen.is_dir():
        raise NotADirectoryError(
            "La ruta indicada corresponde a un directorio; indica un archivo de texto del proyecto."
        )
    return origen.read_text(encoding=encoding)


def abrir_archivo_desde_ruta_validada(
    ruta: str | Path, estado: GuiFileState
) -> tuple[str, str]:
    """Abre un archivo cuya ruta ya fue validada contra project_root."""

    origen = Path(ruta).expanduser().resolve()
    contenido = leer_archivo_texto_validado(origen)
    estado.ruta = origen
    estado.contenido_cargado = contenido
    estado.cambios_sin_guardar = False
    return contenido, f"Archivo cargado: {origen}"


def recargar_archivo_activo_validado(
    estado: GuiFileState,
) -> tuple[str, str]:
    """Recarga el archivo activo cuya ruta ya fue validada contra project_root."""

    if estado.ruta is None:
        raise ValueError("No hay archivo activo que recargar.")

    origen = Path(estado.ruta).expanduser().resolve()
    contenido = leer_archivo_texto_validado(origen)
    estado.ruta = origen
    estado.contenido_cargado = contenido
    estado.cambios_sin_guardar = False
    return contenido, f"Archivo cargado: {origen}"


def recargar_archivo_activo(estado: GuiFileState) -> tuple[str, str]:
    """Recarga el archivo activo desde disco y devuelve contenido/mensaje."""

    if estado.ruta is None:
        raise ValueError("No hay archivo activo que recargar.")
    return abrir_archivo_desde_ruta(estado.ruta, estado)


def cargar_archivo_desde_arbol(
    ruta: str | Path, estado: GuiFileState
) -> tuple[str, str]:
    """Carga una entrada de árbol si es archivo Cobra y devuelve contenido/mensaje."""

    if not es_archivo_cobra(ruta):
        raise ValueError("Selecciona un archivo Cobra (.co o .cobra).")
    return abrir_archivo_desde_ruta(ruta, estado)


def require_flet() -> Any:
    """Importa Flet de forma diferida para no romper imports de CLI."""
    try:
        import flet as ft
    except ModuleNotFoundError as exc:  # pragma: no cover - validado desde CLI
        raise RuntimeError(
            "Falta la dependencia 'flet'. Ejecuta: pip install flet."
        ) from exc
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


def _crear_boton_motor_ia(ft: Any, texto: str, *, on_click: Any) -> Any:
    """Crea un botón dependiente del motor IA opcional de sugerencias."""

    motor = detectar_motor_ia_sugerencias()
    return flet_elevated_button(
        ft,
        texto,
        on_click=on_click if motor.disponible else None,
        disabled=not motor.disponible,
        tooltip=motor.tooltip,
    )


def crear_boton_sugerencias_libro(ft: Any, *, on_click: Any) -> Any:
    """Crea el botón de sugerencias con estado visual según motor IA."""

    return _crear_boton_motor_ia(ft, SUGERENCIAS_BUTTON_TEXT, on_click=on_click)


def crear_boton_correccion(ft: Any, *, on_click: Any) -> Any:
    """Crea el botón visible de corrección sin modificar automáticamente el editor."""

    return _crear_boton_motor_ia(ft, CORRECCION_BUTTON_TEXT, on_click=on_click)


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


def crear_arbol_directorios(
    ft: Any, *, on_click: Any, root_path: str | Path | None = None
) -> Any:
    """Crea un árbol de directorios con carga diferida de subcarpetas.

    Si no se proporciona ``root_path``, usa la raíz de trabajo canónica del
    IDLE como fallback explícito en lugar de depender del directorio actual del
    proceso.
    """
    if root_path is None:
        root_path = resolver_workspace_root_idle()

    def _crear_nodo_archivo(path: Path) -> Any:
        return ft.ListTile(
            title=ft.Text(path.name),
            leading=ft.Icon(ft.Icons.INSERT_DRIVE_FILE),
            data=str(path),
            on_click=on_click,
        )

    def _crear_nodo_directorio(path: Path) -> Any:
        tile = ft.ExpansionTile(
            title=ft.Text(path.name),
            leading=ft.Icon(ft.Icons.FOLDER),
            controls=[],
        )
        tile.data = {"path": path, "children_loaded": False}

        def _cargar_hijos_al_expandir(_e: Any) -> None:
            data = getattr(tile, "data", {})
            if data.get("children_loaded"):
                return
            tile.controls = [
                _crear_nodo(entrada) for entrada in listar_directorio_idle(path)
            ]
            data["children_loaded"] = True
            tile.data = data
            update = getattr(tile, "update", None)
            if callable(update):
                update()

        tile.on_change = _cargar_hijos_al_expandir
        return tile

    def _crear_nodo(path: Path) -> Any:
        if path.is_dir():
            return _crear_nodo_directorio(path)
        return _crear_nodo_archivo(path)

    entradas = listar_directorio_idle(root_path)
    if not entradas:
        return ft.Column(
            [flet_text(ft, value="No hay archivos visibles en esta carpeta")],
            scroll=ft.ScrollMode.ALWAYS,
        )

    elementos_arbol = [_crear_nodo(entrada) for entrada in entradas]

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


def ejecutar_o_transpilar(
    codigo: str, *, transpilacion_activa: bool, target: str
) -> str:
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


def _guardar_archivo(
    page: Any, entrada: Any, estado_archivo: GuiFileState, ruta: Path
) -> None:
    """Guarda el editor usando la misma lógica y mensajes de ``Guardar como``."""
    flet_runtime = require_flet()
    try:
        _contenido, mensaje = guardar_archivo_como(ruta, entrada.value, estado_archivo)
        page.snack_bar.open = True
        page.snack_bar.content = flet_text(flet_runtime, mensaje)
    except Exception as exc:
        page.snack_bar.open = True
        page.snack_bar.content = flet_text(flet_runtime, f"Error al guardar: {exc}")
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
            crear_handler_guardar_como(
                entrada=entrada, estado_archivo=estado_archivo, page=page
            )(_e)

    return guardar_handler


def crear_handler_guardar_como(
    *,
    entrada: Any,
    estado_archivo: GuiFileState,
    page: Any,
) -> Any:
    """Crea un helper de ``Guardar como`` basado en ``FilePicker``.

    El flujo canónico del IDLE principal conserva el campo ``Ruta`` para que
    abrir, guardar como y la ruta activa compartan una única entrada visible.
    Este helper queda disponible para integraciones GUI alternativas que
    prefieran delegar la selección de destino al diálogo nativo de Flet.
    """

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
            dialog_title="Guardar archivo del proyecto",
            file_name="nuevo_archivo.cobra",
            allowed_extensions=["cobra", "co"],
        )

    return guardar_como_handler


def analizar_codigo(codigo: str) -> tuple[list[Any], Any]:
    """Ejecuta Lexer y Parser una vez y devuelve tokens y AST."""

    deps = require_gui_dependencies()
    tokens = deps["Lexer"](codigo).tokenizar()
    ast = deps["Parser"](tokens).parsear()
    return tokens, ast


_CATEGORIAS_SUGERENCIAS = (
    ("léxico/sintaxis", "Léxico/sintaxis"),
    ("estilo", "Estilo"),
    ("nombres", "Nombres"),
    ("forma canónica", "Forma canónica"),
    ("observabilidad", "Observabilidad"),
)


def _categoria_sugerencia(sugerencia: str) -> str:
    """Clasifica una sugerencia del Libro para mostrarla agrupada en GUI."""

    texto = sugerencia.lower()
    if "lp-3.1-nombres" in texto or "nombres descriptivos" in texto:
        return "nombres"
    if "lp-3.3-impresion" in texto or "imprimir" in texto:
        return "observabilidad"
    if "lp-3.3-retorno" in texto or "retorno" in texto or "retornar" in texto:
        return "forma canónica"
    if "lp-3.9-funciones" in texto or "funcion" in texto:
        return "léxico/sintaxis"
    if "lp-3.6-usar" in texto or "usar" in texto or "alias" in texto:
        return "estilo"
    return "estilo"


def _formatear_sugerencias_agrupadas(sugerencias: list[str]) -> str:
    """Devuelve sugerencias visibles agrupadas por tipo pedagógico."""

    agrupadas = {clave: [] for clave, _titulo in _CATEGORIAS_SUGERENCIAS}
    for sugerencia in sugerencias:
        agrupadas[_categoria_sugerencia(sugerencia)].append(sugerencia)

    bloques: list[str] = []
    for clave, titulo in _CATEGORIAS_SUGERENCIAS:
        items = agrupadas[clave]
        if items:
            cuerpo = "\n".join(f"  - {item}" for item in items)
        else:
            cuerpo = "  - Sin sugerencias."
        bloques.append(f"- {titulo}:\n{cuerpo}")
    return "\n".join(bloques)


def _extraer_metadatos_sugerencia(sugerencia: str) -> tuple[str, str]:
    """Extrae regla y sección del Libro si el motor las incluye en el texto."""

    regla = "regla no especificada"
    seccion = "sección no especificada"
    match = re.search(r"\[regla:\s*([^;\]]+)(?:;\s*([^\]]+))?\]", sugerencia)
    if match:
        regla = match.group(1).strip()
        if match.group(2):
            seccion = match.group(2).strip()
    else:
        seccion_match = re.search(r"(§\s*\d+(?:\.\d+)?[^:;\]]*)", sugerencia)
        if seccion_match:
            seccion = seccion_match.group(1).strip()
    return regla, seccion


def _ubicacion_aproximada_sugerencia(codigo: str, sugerencia: str) -> str:
    """Calcula una ubicación aproximada sin alterar el editor."""

    texto = sugerencia.lower()
    pistas = (
        ("retorno", ("retornar", "retorno")),
        ("función", ("funcion ", "func ", "definir ")),
        ("módulo", ("usar ",)),
        ("impresión", ("imprimir",)),
        (
            "nombre",
            (
                "var ",
                "=",
            ),
        ),
    )
    for _nombre, patrones in pistas:
        if any(patron.strip() in texto for patron in patrones):
            for numero, linea in enumerate(codigo.splitlines(), start=1):
                linea_normalizada = linea.lower()
                if any(patron in linea_normalizada for patron in patrones):
                    return f"línea {numero}"
    return "ubicación no disponible"


def _limpiar_explicacion_sugerencia(sugerencia: str) -> str:
    """Elimina metadatos compactos para dejar una explicación legible."""

    return re.sub(r"\s*\[regla:[^\]]+\]\s*$", "", sugerencia).strip() or sugerencia


def _formatear_sugerencias_detalladas(codigo: str, sugerencias: list[str]) -> str:
    """Devuelve una lista agrupada con regla, sección, ubicación y explicación."""

    agrupadas = {clave: [] for clave, _titulo in _CATEGORIAS_SUGERENCIAS}
    for sugerencia in sugerencias:
        regla, seccion = _extraer_metadatos_sugerencia(sugerencia)
        ubicacion = _ubicacion_aproximada_sugerencia(codigo, sugerencia)
        explicacion = _limpiar_explicacion_sugerencia(sugerencia)
        item = (
            f"  - Regla: {regla} | Sección: {seccion} | "
            f"Ubicación: {ubicacion} | Explicación: {explicacion}"
        )
        agrupadas[_categoria_sugerencia(sugerencia)].append(item)

    bloques: list[str] = []
    for clave, titulo in _CATEGORIAS_SUGERENCIAS:
        items = agrupadas[clave]
        cuerpo = "\n".join(items) if items else "  - Sin sugerencias."
        bloques.append(f"- {titulo}:\n{cuerpo}")
    return "\n".join(bloques)


def generar_reporte_correccion_tipografica(codigo: str) -> str:
    """Valida código y genera un reporte de corrección sin editar automáticamente."""

    deps = require_gui_dependencies()
    try:
        analizar_codigo(codigo)
    except Exception as exc:
        error = formatear_error(
            exc,
            lexer_error_type=deps.get("LexerError"),
            parser_error_type=deps.get("ParserError"),
        )
        return (
            "Errores léxicos/sintácticos:\n"
            f"- {error}\n\n"
            "Corrección tipográfica del Libro:\n"
            "- Corrige primero los errores anteriores para solicitar sugerencias."
        )

    motor = detectar_motor_ia_sugerencias()
    if not motor.disponible:
        return (
            "Errores léxicos/sintácticos:\n"
            "- No se detectaron errores con el Lexer y Parser de Cobra.\n\n"
            "Corrección tipográfica del Libro:\n"
            f"- {motor.tooltip}"
        )

    try:
        sugerencias = generar_sugerencias(codigo)
    except ImportError as exc:
        return (
            "Errores léxicos/sintácticos:\n"
            "- No se detectaron errores con el Lexer y Parser de Cobra.\n\n"
            "Corrección tipográfica del Libro:\n"
            f"- No se pudieron generar sugerencias: {exc}. "
            "Instala la dependencia opcional de sugerencias para activar esta acción."
        )

    if sugerencias:
        sugerencias_legibles = _formatear_sugerencias_detalladas(codigo, sugerencias)
    else:
        sugerencias_legibles = "- No se recibieron sugerencias."
    return (
        "Errores léxicos/sintácticos:\n"
        "- No se detectaron errores con el Lexer y Parser de Cobra.\n\n"
        "Corrección tipográfica del Libro:\n"
        f"{sugerencias_legibles}\n\n"
        "Nota: el editor no se modifica automáticamente."
    )


def generar_reporte_sugerencias(codigo: str) -> str:
    """Valida código y genera reporte común de sugerencias estilísticas."""

    deps = require_gui_dependencies()
    try:
        analizar_codigo(codigo)
    except Exception as exc:
        error = formatear_error(
            exc,
            lexer_error_type=deps.get("LexerError"),
            parser_error_type=deps.get("ParserError"),
        )
        return (
            "Errores léxicos/sintácticos:\n"
            f"- {error}\n\n"
            "Sugerencias del Libro:\n"
            "- Corrige primero los errores anteriores para solicitar sugerencias."
        )

    motor = detectar_motor_ia_sugerencias()
    if not motor.disponible:
        return (
            "Errores léxicos/sintácticos:\n"
            "- No se detectaron errores con el Lexer y Parser de Cobra.\n\n"
            "Sugerencias del Libro:\n"
            f"- {motor.tooltip}"
        )

    try:
        sugerencias = generar_sugerencias(codigo)
    except ImportError as exc:
        return (
            "Errores léxicos/sintácticos:\n"
            "- No se detectaron errores con el Lexer y Parser de Cobra.\n\n"
            "Sugerencias del Libro:\n"
            f"- No se pudieron generar sugerencias: {exc}. "
            "Instala la dependencia opcional de sugerencias para activar esta acción."
        )

    if sugerencias:
        sugerencias_legibles = _formatear_sugerencias_agrupadas(sugerencias)
    else:
        sugerencias_legibles = "- No se recibieron sugerencias."
    return (
        "Errores léxicos/sintácticos:\n"
        "- No se detectaron errores con el Lexer y Parser de Cobra.\n\n"
        "Sugerencias del Libro:\n"
        f"{sugerencias_legibles}"
    )


def crear_handler_tokens(*, entrada: Any, salida: Any, page: Any) -> Any:
    """Crea handler compartido para mostrar tokens Cobra."""

    def tokens_handler(_e: Any) -> None:
        deps = require_gui_dependencies()
        try:
            salida.value = mostrar_tokens(normalizar_codigo(entrada.value))
        except Exception as exc:
            salida.value = formatear_error(
                exc,
                lexer_error_type=deps.get("LexerError"),
                parser_error_type=deps.get("ParserError"),
            )
        finally:
            page.update()

    return tokens_handler


def crear_handler_ast(*, entrada: Any, salida: Any, page: Any) -> Any:
    """Crea handler compartido para mostrar el AST Cobra."""

    def ast_handler(_e: Any) -> None:
        deps = require_gui_dependencies()
        try:
            salida.value = mostrar_ast(normalizar_codigo(entrada.value))
        except Exception as exc:
            salida.value = formatear_error(
                exc,
                lexer_error_type=deps.get("LexerError"),
                parser_error_type=deps.get("ParserError"),
            )
        finally:
            page.update()

    return ast_handler


def crear_handler_correccion_tipografica(
    *, entrada: Any, salida: Any, page: Any
) -> Any:
    """Crea handler para corrección tipográfica validada y no destructiva."""

    def correccion_handler(_e: Any) -> None:
        deps = require_gui_dependencies()
        try:
            salida.value = generar_reporte_correccion_tipografica(
                normalizar_codigo(entrada.value)
            )
        except Exception as exc:
            salida.value = formatear_error(
                exc,
                lexer_error_type=deps.get("LexerError"),
                parser_error_type=deps.get("ParserError"),
            )
        finally:
            page.update()

    return correccion_handler


def crear_handler_sugerencias(*, entrada: Any, salida: Any, page: Any) -> Any:
    """Crea handler compartido para sugerencias con validación léxica/sintáctica."""

    def sugerencias_handler(_e: Any) -> None:
        deps = require_gui_dependencies()
        try:
            salida.value = generar_reporte_sugerencias(normalizar_codigo(entrada.value))
        except Exception as exc:
            salida.value = formatear_error(
                exc,
                lexer_error_type=deps.get("LexerError"),
                parser_error_type=deps.get("ParserError"),
            )
        finally:
            page.update()

    return sugerencias_handler


# Compatibilidad interna: conservar temporalmente el nombre antiguo sin
# recomendarlo como API de GUI. La ruta canónica es crear_handler_sugerencias.
def crear_handler_sugerencias_agix(
    *,
    entrada: Any,
    salida: Any,
    page: Any,
) -> Any:
    """Alias interno de compatibilidad; usar ``crear_handler_sugerencias``."""

    warnings.warn(
        "crear_handler_sugerencias_agix está deprecado; usa crear_handler_sugerencias.",
        DeprecationWarning,
        stacklevel=2,
    )
    return crear_handler_sugerencias(entrada=entrada, salida=salida, page=page)


def normalizar_codigo(codigo: str | None) -> str:
    """Normaliza la entrada para evitar valores ``None``."""
    return codigo or ""


def ejecutar_codigo(codigo: str) -> str:
    """Ejecuta código Cobra y captura la salida impresa."""
    deps = require_gui_dependencies()
    buffer = io.StringIO()
    with redirect_stdout(buffer), redirect_stderr(buffer):
        _tokens, ast = analizar_codigo(codigo)
        deps["InterpretadorCobra"]().ejecutar_ast(ast)
    return buffer.getvalue()


def transpilar_codigo(codigo: str, lang: str) -> str:
    """Transpila código Cobra al lenguaje especificado."""
    deps = require_gui_dependencies()
    _tokens, ast = analizar_codigo(codigo)
    transp = deps["TRANSPILERS"][lang]()
    return transp.generate_code(ast)


def mostrar_tokens(codigo: str) -> str:
    deps = require_gui_dependencies()
    tokens, _ast = analizar_codigo(codigo)
    return "\n".join(str(token) for token in tokens)


def mostrar_ast(codigo: str) -> str:
    """Parsea código Cobra y devuelve una representación serializada del AST."""
    deps = require_gui_dependencies()
    _tokens, ast = analizar_codigo(codigo)
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
    return deps["target_cli_choices"](set(PUBLIC_BACKENDS) & set(deps["TRANSPILERS"]))
