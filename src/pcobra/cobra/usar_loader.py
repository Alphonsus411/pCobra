import importlib
import importlib.util
import logging
import os
import re
from pathlib import Path
import sys
from typing import Any

from pcobra.cobra.imports.resolver import CobraImportResolver, ImportResolutionError
from pcobra.cobra.usar_policy import (
    CANONICAL_MODULE_SURFACE_CONTRACTS,
    REPL_COBRA_MODULE_INTERNAL_PATH_MAP,
    USAR_BACKEND_BLOCKLIST,
    USAR_COBRA_PUBLIC_MODULES,
    USAR_RUNTIME_EXPORT_OVERRIDES,
)
from pcobra.cobra.core.usar_symbol_policy import (
    build_and_validate_usar_symbol_metadata,
    depuracion_saneamiento_usar_habilitada,
    sanear_exportables_para_usar,
)

# Regex estricta para mantener la sintaxis `usar "modulo"` acotada a identificadores simples.
_VALID_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


# Segmentos seguros para módulos de proyecto: ruta lógica punteada, no ruta del sistema.
_VALID_PROJECT_MODULE_SEGMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_PROJECT_MODULE_FORBIDDEN_CHARS = frozenset('/\\@$%*?"\'<>|;`!()[]{}=+,')
_USAR_PROJECT_MODULE_CACHE: dict[tuple[Path, bool], dict[str, Any]] = {}
_USAR_PROJECT_LOADING_STACK: list[Path] = []
_IMPORT_CO_AST_CACHE: dict[Path, list[Any]] = {} # Nueva caché para ASTs de .co

# Patrones que deben bloquearse explícitamente para evitar imports de backend o rutas internas.
_INTERNAL_HINTS = (
    "pcobra",
    "cobra",
    "core",
    "corelibs",
    "standard_library",
    "backend",
    "sdk",
    "holobit_sdk",
    "bindings",
    "runtime",
    "transpilers",
    "transpiler",
)

_BACKEND_PREFIXES = (
    "backend",
    "pcobra",
    "cobra",
    "core",
    "corelibs",
    "runtime",
)

_BACKEND_EQUIVALENTS = {
    "nodefetch",
    "node_fetch",
    "serde",
    "holobitsdk",
    "holobit_sdk",
}


class UsarExports(dict):
    """Mapa de exports compatible con API directa y metadata estructurada."""

    def __eq__(self, other: object) -> bool:
        if isinstance(other, dict) and not {"simbolos", "metadata"} & set(other):
            return {
                nombre: self[nombre]
                for nombre in self
                if nombre not in {"simbolos", "metadata"}
            } == other
        return super().__eq__(other)


def _construir_exports_usar(
    simbolos: list[tuple[str, Any]],
    metadata: dict[str, dict[str, Any]],
) -> UsarExports:
    exports = UsarExports({"simbolos": simbolos, "metadata": metadata})
    exports.update(dict(simbolos))
    return exports


def normalizar_nombre_usar(nombre: str) -> str:
    """Normaliza nombre de módulo para validaciones canónicas de `usar`."""

    return (nombre or "").strip().lower().replace("-", "_")


def _rechazar_modulo_no_canonico(nombre: str) -> None:
    """Rechaza módulos backend/no-canónicos con error explícito para `usar`."""

    nombre_normalizado = normalizar_nombre_usar(nombre)
    blocklist_normalizada = {normalizar_nombre_usar(item) for item in USAR_BACKEND_BLOCKLIST}
    equivalentes_normalizados = {normalizar_nombre_usar(item) for item in _BACKEND_EQUIVALENTS}

    if nombre_normalizado in blocklist_normalizada or nombre_normalizado in equivalentes_normalizados:
        raise PermissionError(
            f"Importación no permitida en 'usar': '{nombre}'. "
            "Es un módulo backend/no canónico y no forma parte de la API pública. "
            f"Módulos permitidos: {', '.join(USAR_COBRA_PUBLIC_MODULES)}."
        )

    if any(
        nombre_normalizado == prefijo or nombre_normalizado.startswith(f"{prefijo}_")
        for prefijo in _BACKEND_PREFIXES
    ):
        raise PermissionError(
            f"Importación no permitida en 'usar': '{nombre}'. "
            "Es un módulo backend/no canónico y no forma parte de la API pública. "
            f"Módulos permitidos: {', '.join(USAR_COBRA_PUBLIC_MODULES)}."
        )

def validar_nombre_modulo_usar(nombre: str, *, require_allowlist: bool = True) -> str:
    """Valida nombre de `usar` y opcionalmente exige contrato canónico exacto."""

    if not isinstance(nombre, str):
        raise ValueError("Nombre de módulo inválido en 'usar': se esperaba string.")

    nombre_raw = nombre.strip()
    if not nombre_raw:
        raise ValueError("Nombre de módulo vacío en 'usar'.")

    if any(sep in nombre_raw for sep in ('/', '\\')) or '..' in nombre_raw:
        raise ValueError(
            f"Nombre de módulo inválido en 'usar': '{nombre_raw}' parece ruta/traversal."
        )

    _rechazar_modulo_no_canonico(nombre_raw)
    nombre = normalizar_nombre_usar(nombre_raw)

    if not _VALID_NAME_RE.fullmatch(nombre):
        raise ValueError(
            "Nombre de módulo inválido en 'usar': solo se permiten "
            "identificadores simples en minúsculas (ej. usar 'texto')."
        )

    if any(ch in nombre for ch in ("/", "\\", ".", "-", ":", "@")):
        raise ValueError(f"Nombre de módulo '{nombre}' no es seguro para 'usar'.")

    for hint in _INTERNAL_HINTS:
        if hint in nombre:
            raise ValueError(
                f"Nombre de módulo '{nombre}' parece una ruta interna o de backend; "
                "usa únicamente módulos Cobra canónicos."
            )

    if require_allowlist and nombre not in USAR_COBRA_PUBLIC_MODULES:
        raise PermissionError(
            f"usar_error[modulo_fuera_catalogo_publico]: '{nombre}' está fuera del catálogo público."
        )

    return nombre



def validar_nombre_modulo_cobra_proyecto(nombre: str) -> tuple[str, ...]:
    """Valida una ruta lógica punteada de módulo Cobra de proyecto.

    Esta validación es deliberadamente independiente de
    :func:`validar_nombre_modulo_usar` para no relajar el contrato público de
    módulos oficiales/corelibs.
    """

    if not isinstance(nombre, str):
        raise ValueError("Nombre de módulo de proyecto inválido: se esperaba string.")

    nombre_raw = nombre.strip()
    if not nombre_raw:
        raise ValueError("Nombre de módulo de proyecto vacío.")

    if any(sep in nombre_raw for sep in ("/", "\\")):
        raise ValueError(
            f"Nombre de módulo de proyecto inválido: '{nombre_raw}' no debe contener separadores de ruta."
        )

    segmentos = nombre_raw.split(".")
    for segmento in segmentos:
        if segmento in {"", ".", ".."}:
            raise ValueError(
                f"Nombre de módulo de proyecto inválido: '{nombre_raw}' contiene segmentos vacíos/traversal."
            )
        if any(caracter in segmento for caracter in _PROJECT_MODULE_FORBIDDEN_CHARS):
            raise ValueError(
                f"Nombre de módulo de proyecto inválido: '{nombre_raw}' contiene caracteres no seguros."
            )
        if ":" in segmento:
            raise ValueError(
                f"Nombre de módulo de proyecto inválido: '{nombre_raw}' parece una unidad Windows."
            )
        if not _VALID_PROJECT_MODULE_SEGMENT_RE.fullmatch(segmento):
            raise ValueError(
                "Nombre de módulo de proyecto inválido: usa segmentos tipo identificador "
                "separados por puntos (ej. 'utilidades.fechas')."
            )

    return tuple(segmentos)


def _verificar_path_dentro_de_root(ruta: Path, root: Path) -> None:
    """Verifica con rutas canónicas que ``ruta`` queda dentro de ``root``."""

    try:
        common = os.path.commonpath((str(root), str(ruta)))
    except ValueError as exc:
        raise ValueError("Ruta de módulo de proyecto fuera de la raíz autorizada.") from exc

    if common != str(root):
        raise ValueError("Ruta de módulo de proyecto fuera de la raíz autorizada.")


def resolver_modulo_cobra_proyecto(
    nombre: str,
    *,
    project_root: Path,
    current_file: Path | None = None,
) -> Path:
    """Resuelve un módulo Cobra de proyecto a un archivo ``.co`` seguro.

    ``nombre`` es una ruta lógica punteada (por ejemplo
    ``utilidades.fechas``), que se transforma en
    ``project_root / "utilidades" / "fechas.co"``. La función sólo devuelve
    una ruta canónica; no carga ni importa el módulo para evitar introducir un
    segundo sistema de imports.
    """

    validar_nombre_modulo_cobra_proyecto(nombre)
    root_resuelto = canonicalizar_ruta_usar_proyecto(project_root)

    if current_file is not None:
        current_resuelto = canonicalizar_ruta_usar_proyecto(current_file)
        _verificar_path_dentro_de_root(current_resuelto, root_resuelto)

    try:
        resolution = CobraImportResolver(
            project_root=root_resuelto,
            collision_policy="warn",
        ).resolve(nombre)
    except ImportResolutionError as exc:
        if exc.code == "IMP-PROJECT-PATH-001":
            raise ValueError("Ruta de módulo de proyecto fuera de la raíz autorizada.") from exc
        raise FileNotFoundError(f"Módulo no encontrado: {nombre}") from exc

    if resolution.source != "project" or not resolution.file_path:
        raise FileNotFoundError(f"Módulo no encontrado: {nombre}")

    ruta_resuelta = Path(resolution.file_path)
    _verificar_path_dentro_de_root(ruta_resuelta, root_resuelto)

    return ruta_resuelta


def canonicalizar_ruta_usar_proyecto(ruta: str | Path) -> Path:
    """Devuelve la clave canónica de caché para módulos Cobra de proyecto."""

    return Path(ruta).expanduser().resolve(strict=False)


def resolver_ruta_canonica_modulo_cobra_proyecto(
    nombre: str,
    *,
    project_root: Path,
    current_file: Path | None = None,
) -> Path:
    """Resuelve un módulo de proyecto y normaliza su ruta como clave de caché."""

    return canonicalizar_ruta_usar_proyecto(
        resolver_modulo_cobra_proyecto(
            nombre,
            project_root=project_root,
            current_file=current_file,
        )
    )


def obtener_cache_modulos_cobra_proyecto() -> dict[tuple[Path, bool], dict[str, Any]]:
    """Expone la caché compartida de módulos de proyecto para el intérprete."""

    return _USAR_PROJECT_MODULE_CACHE


def obtener_pila_carga_modulos_cobra_proyecto() -> list[Path]:
    """Expone la pila compartida de carga para detectar ciclos entre entrypoints."""

    return _USAR_PROJECT_LOADING_STACK


def obtener_cache_ast_import_co() -> dict[Path, list[Any]]:
    """Expone la caché compartida de ASTs de módulos .co para el transpilador."""
    return _IMPORT_CO_AST_CACHE


def formatear_ciclo_modulos_cobra_proyecto(ruta_modulo: Path) -> str:
    """Construye una cadena clara del ciclo usando rutas canónicas en la pila."""

    ruta_canonica = canonicalizar_ruta_usar_proyecto(ruta_modulo)
    pila = [canonicalizar_ruta_usar_proyecto(ruta) for ruta in _USAR_PROJECT_LOADING_STACK]
    ciclo = [*pila, ruta_canonica]
    inicio = ciclo.index(ruta_canonica)
    return " -> ".join(ruta.name for ruta in ciclo[inicio:])


def _ascender_hasta_cobra_toml(candidato: Path | None) -> Path | None:
    """Busca ``cobra.toml`` ascendiendo desde un archivo o directorio."""

    if candidato is None:
        return None
    ruta = Path(candidato).expanduser().resolve(strict=False)
    if ruta.suffix or (ruta.exists() and ruta.is_file()):
        ruta = ruta.parent
    for directorio in (ruta, *ruta.parents):
        if (directorio / "cobra.toml").is_file():
            return directorio.resolve(strict=False)
    return None


def descubrir_raiz_proyecto(start: Path | None, main_file: Path | None = None) -> Path:
    """Descubre y canonicaliza la raíz efectiva de un proyecto Cobra.

    Prioridad:
    1. Directorio que contiene un ``cobra.toml`` encontrado ascendiendo desde
       ``start`` o desde ``main_file``.
    2. Directorio canonicalizado de ``main_file`` cuando no hay ``cobra.toml``.
    3. ``Path.cwd().resolve()`` para preservar el comportamiento legacy.
    """

    for candidato in (start, main_file):
        raiz_configurada = _ascender_hasta_cobra_toml(candidato)
        if raiz_configurada is not None:
            return raiz_configurada

    if main_file is not None:
        principal = Path(main_file).expanduser().resolve(strict=False)
        directorio = principal.parent if principal.suffix or principal.is_file() else principal
        return directorio.resolve(strict=False)

    return Path.cwd().resolve()


def _cargar_modulo_local_desde_directorio(nombre: str, directorio: Path):
    """Carga un módulo Python desde un directorio local dado."""

    mod_path = directorio / f"{nombre}.py"
    pkg_path = directorio / nombre / "__init__.py"
    if not (mod_path.exists() or pkg_path.exists()):
        return None

    ruta = mod_path if mod_path.exists() else pkg_path
    mod_spec = importlib.util.spec_from_file_location(nombre, ruta)
    if mod_spec is None or mod_spec.loader is None:
        raise ImportError(f"No se pudo crear spec para el módulo '{nombre}'")
    modulo = importlib.util.module_from_spec(mod_spec)
    sys.modules[nombre] = modulo
    mod_spec.loader.exec_module(modulo)
    return modulo


def _cargar_modulo_local_desde_ruta(nombre: str, ruta: Path):
    """Carga un módulo Python desde una ruta absoluta explícita."""

    modulo_existente = sys.modules.get(nombre)
    if modulo_existente is not None:
        modulo_file = getattr(modulo_existente, "__file__", None)
        if modulo_file and Path(modulo_file).resolve() == ruta:
            return modulo_existente

    mod_spec = importlib.util.spec_from_file_location(nombre, ruta)
    if mod_spec is None or mod_spec.loader is None:
        raise ImportError(f"No se pudo crear spec para el módulo '{nombre}'")
    modulo = importlib.util.module_from_spec(mod_spec)
    sys.modules[nombre] = modulo
    mod_spec.loader.exec_module(modulo)
    return modulo


def obtener_modulo_cobra_oficial(nombre: str):
    """Carga módulos oficiales de Cobra desde la ruta interna canónica declarada."""

    nombre = validar_nombre_modulo_usar(nombre, require_allowlist=True)
    rel_path = REPL_COBRA_MODULE_INTERNAL_PATH_MAP.get(nombre)
    if not rel_path:
        raise ModuleNotFoundError(
            f"Módulo oficial Cobra '{nombre}' permitido pero sin ruta interna canónica declarada."
        )

    repo_root = Path(__file__).resolve().parents[3]
    ruta_modulo = (repo_root / rel_path).resolve()
    if not ruta_modulo.exists():
        raise ModuleNotFoundError(
            "Módulo oficial Cobra permitido no resoluble en runtime: "
            f"alias='{nombre}' ruta='{rel_path}'."
        )

    if rel_path.startswith("src/pcobra/corelibs/"):
        nombre_import = f"pcobra.corelibs.{ruta_modulo.stem}"
    elif rel_path.startswith("src/pcobra/standard_library/"):
        nombre_import = f"pcobra.standard_library.{ruta_modulo.stem}"
    else:
        nombre_import = ""

    if nombre_import:
        modulo = importlib.import_module(nombre_import)
        modulo_file = getattr(modulo, "__file__", None)
        if modulo_file and Path(modulo_file).resolve() == ruta_modulo:
            for export_name in getattr(modulo, "__all__", ()):  # Cobra-facing: alias público.
                export = getattr(modulo, export_name, None)
                if callable(export) and hasattr(export, "__module__"):
                    try:
                        export.__module__ = nombre
                    except (AttributeError, TypeError):
                        pass
            return modulo

    return _cargar_modulo_local_desde_ruta(nombre, ruta_modulo)


def obtener_modulo(nombre: str, *, permitir_instalacion: bool = True):
    """Resuelve módulos de `usar` solo contra la allowlist canónica de Cobra."""

    _ = permitir_instalacion  # compat: ya no se usa instalación dinámica para `usar`.
    nombre = validar_nombre_modulo_usar(nombre, require_allowlist=True)

    try:
        return obtener_modulo_cobra_oficial(nombre)
    except ModuleNotFoundError as exc:
        raise ImportError(
            f"No se pudo resolver el módulo Cobra permitido '{nombre}' en runtime."
        ) from exc


def _extraer_exports_modulo_cobra_proyecto(
    ast: list[object],
    entorno_modulo: object,
    *,
    ruta_modulo: Path,
) -> dict[str, Any]:
    """Extrae exports saneados de un módulo ``.co`` ya ejecutado."""

    from pcobra.core.ast_nodes import NodoExport

    valores_entorno = getattr(entorno_modulo, "values", {})
    nombres_exportados = [
        nodo.nombre for nodo in ast if isinstance(nodo, NodoExport)
    ] or [nombre for nombre in valores_entorno if not nombre.startswith("_")]

    simbolos_saneados: list[tuple[str, object]] = []
    metadata_por_simbolo: dict[str, dict[str, object]] = {}
    modulo_canonico = str(ruta_modulo.resolve(strict=False))
    for nombre in nombres_exportados:
        if nombre not in valores_entorno:
            continue
        simbolo = valores_entorno[nombre]
        simbolos_saneados.append((nombre, simbolo))
        metadata_por_simbolo[nombre] = build_and_validate_usar_symbol_metadata(
            module_name=modulo_canonico,
            symbol_name=nombre,
            callable_obj=simbolo,
        )

    return {
        "simbolos": simbolos_saneados,
        "metadata": metadata_por_simbolo,
    }


def _cargar_exports_modulo_cobra_proyecto(
    nombre: str,
    *,
    project_root: Path,
    current_file: Path | None = None,
    safe_mode: bool = False,
) -> dict[str, Any]:
    """Carga un módulo Cobra de proyecto usando resolución canónica y cache."""

    from pcobra.core.environment import Environment
    from pcobra.core.import_utils import cargar_ast_modulo
    from pcobra.core.interpreter import InterpretadorCobra
    from pcobra.core.ast_nodes import NodoExport

    ruta_modulo = resolver_ruta_canonica_modulo_cobra_proyecto(
        nombre,
        project_root=project_root,
        current_file=current_file,
    )

    clave_cache = (ruta_modulo, safe_mode)
    if clave_cache in _USAR_PROJECT_MODULE_CACHE:
        return _USAR_PROJECT_MODULE_CACHE[clave_cache]

    if ruta_modulo in _USAR_PROJECT_LOADING_STACK:
        cadena = formatear_ciclo_modulos_cobra_proyecto(ruta_modulo)
        raise ImportError(f"Ciclo de módulos detectado en usar: {cadena}")

    try:
        ast = cargar_ast_modulo(
            str(ruta_modulo),
            modules_path=str(project_root),
            whitelist={project_root},
        )
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Módulo no encontrado: {nombre}") from exc

    interpretador = InterpretadorCobra(
        safe_mode=safe_mode, main_file=current_file or ruta_modulo
    )
    interpretador._project_root = canonicalizar_ruta_usar_proyecto(project_root)
    interpretador._main_file = (
        canonicalizar_ruta_usar_proyecto(current_file) if current_file else ruta_modulo
    )
    interpretador._current_module_stack.append(ruta_modulo)
    interpretador.contextos.append(Environment(parent=interpretador.contextos[-1]))
    interpretador.mem_contextos.append({})
    _USAR_PROJECT_LOADING_STACK.append(ruta_modulo)
    try:
        for subnodo in ast:
            if isinstance(subnodo, NodoExport):
                continue
            if safe_mode:
                modo_previo = interpretador._set_mode("analysis")
                try:
                    interpretador._validar(subnodo)
                finally:
                    interpretador._set_mode(modo_previo)
            interpretador.ejecutar_nodo(subnodo)
        exports = _extraer_exports_modulo_cobra_proyecto(
            ast,
            interpretador.contextos[-1],
            ruta_modulo=ruta_modulo,
        )
        _USAR_PROJECT_MODULE_CACHE[clave_cache] = _construir_exports_usar(
            list(exports["simbolos"]),
            {
                nombre: dict(metadata)
                for nombre, metadata in exports["metadata"].items()
            },
        )
        return _USAR_PROJECT_MODULE_CACHE[clave_cache]
    finally:
        memoria_local = interpretador.mem_contextos.pop()
        for idx, tam in memoria_local.values():
            interpretador.liberar_memoria(idx, tam)
        interpretador.contextos.pop()
        interpretador._current_module_stack.pop()
        _USAR_PROJECT_LOADING_STACK.pop()


def usar_modulo(
    nombre: str,
    *,
    project_root: str | Path | None = None,
    current_file: str | Path | None = None,
    safe_mode: bool = False,
) -> dict[str, Any]:
    """API única para resolver ``usar`` en runtime y transpilación Python.

    - Los módulos oficiales preservan ``obtener_modulo`` y devuelven sus
      símbolos públicos saneados.
    - Los módulos Cobra de proyecto (``foo.bar`` -> ``foo/bar.co``) usan la
      misma resolución canónica por ruta y una cache global por archivo.
    """

    if isinstance(nombre, str):
        nombre_limpio = nombre.strip()
        es_modulo_oficial = (
            normalizar_nombre_usar(nombre_limpio) in USAR_COBRA_PUBLIC_MODULES
        )
        if "." in nombre_limpio or not es_modulo_oficial:
            current = (
                Path(current_file).expanduser() if current_file is not None else None
            )
            root = (
                canonicalizar_ruta_usar_proyecto(project_root)
                if project_root is not None
                else descubrir_raiz_proyecto(current, current)
            )
            try:
                exports = _cargar_exports_modulo_cobra_proyecto(
                    nombre_limpio,
                    project_root=root,
                    current_file=current,
                    safe_mode=safe_mode,
                )
                return exports
            except (FileNotFoundError, ValueError) as exc:
                if "." in nombre_limpio:
                    ruta_buscada = root.joinpath(
                        *nombre_limpio.split(".")
                    ).with_suffix(".co")
                    raise FileNotFoundError(
                        f"Módulo no encontrado: {nombre_limpio}. Ruta buscada: {ruta_buscada}"
                    ) from exc

    modulo = obtener_modulo(nombre)
    simbolos_saneados, metadata_por_simbolo, conflictos = sanitizar_exports_publicos(
        modulo,
        normalizar_nombre_usar(nombre),
    )
    if conflictos:
        logging.debug(
            "USAR sanitize conflicts en API única module=%s conflicts=%s",
            nombre,
            conflictos,
        )
    if not simbolos_saneados:
        raise ImportError(f"No se encontraron símbolos exportables para usar '{nombre}'.")
    return _construir_exports_usar(simbolos_saneados, metadata_por_simbolo)


def sanitizar_exports_publicos(modulo: object, alias_modulo: str) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Filtra exports públicos válidos para ``usar`` y reporta conflictos/rechazos.

    Devuelve un mapa limpio ``nombre -> símbolo`` y una lista estructurada de
    conflictos para que el caller pueda advertir y evitar sobreescrituras
    silenciosas.
    """

    contrato = CANONICAL_MODULE_SURFACE_CONTRACTS.get(alias_modulo)
    api_publica_modulo = set(USAR_RUNTIME_EXPORT_OVERRIDES.get(alias_modulo, ()))
    if contrato is not None:
        api_publica_modulo.update(contrato.required_functions)
        api_publica_modulo.update(contrato.allowed_aliases)

    exportables = getattr(modulo, "__all__", None)
    if exportables is None:
        candidatos = list(USAR_RUNTIME_EXPORT_OVERRIDES.get(alias_modulo, ()))
        conflictos = [
            {
                "module": alias_modulo,
                "symbol": "__all__",
                "code": "missing___all__",
                "message": "módulo sin __all__; se aplica whitelist explícita por política",
            }
        ]
    else:
        candidatos = exportables
        conflictos = []

    simbolos_brutos: list[tuple[str, object]] = []
    vistos: set[str] = set()
    depuracion_habilitada = depuracion_saneamiento_usar_habilitada()
    for nombre in candidatos:
        if not isinstance(nombre, str):
            conflictos.append(
                {
                    "module": alias_modulo,
                    "symbol": repr(nombre),
                    "code": "invalid_export_name_type",
                    "message": "nombre de export no es string",
                }
            )
            continue
        if nombre in vistos:
            conflictos.append(
                {
                    "module": alias_modulo,
                    "symbol": nombre,
                    "code": "duplicate_export_name",
                    "message": "nombre exportado repetido en __all__/candidatos",
                }
            )
            continue
        if not hasattr(modulo, nombre):
            conflictos.append(
                {
                    "module": alias_modulo,
                    "symbol": nombre,
                    "code": "missing_export_attr",
                    "message": "el nombre exportado no existe en el módulo",
                }
            )
            continue
        if api_publica_modulo and nombre not in api_publica_modulo:
            conflictos.append(
                {
                    "module": alias_modulo,
                    "symbol": nombre,
                    "code": "outside_public_api",
                    "message": "símbolo descartado por no pertenecer a la API pública canónica",
                }
            )
            if depuracion_habilitada:
                logging.debug(
                    "USAR_SANITIZE_DEBUG %s",
                    {
                        "module": alias_modulo,
                        "symbol": nombre,
                        "reason": "outside_public_api",
                    },
                )
            continue
        vistos.add(nombre)
        simbolos_brutos.append((nombre, getattr(modulo, nombre)))

    simbolos_saneados, clasificacion, warnings = sanear_exportables_para_usar(
        simbolos_brutos,
        modulo_origen=alias_modulo,
    )
    metadata_por_simbolo: dict[str, dict[str, Any]] = {}
    for nombre, simbolo in simbolos_saneados:
        metadata_por_simbolo[nombre] = build_and_validate_usar_symbol_metadata(
            module_name=alias_modulo,
            symbol_name=nombre,
            callable_obj=simbolo,
        )

    for resultado in [*clasificacion.rechazos_duros, *warnings]:
        conflictos.append(
            {
                "module": alias_modulo,
                "symbol": resultado.nombre,
                "code": resultado.codigo or ("warning" if resultado.warning else "rejected"),
                "message": resultado.mensaje or ("warning de saneamiento" if resultado.warning else "símbolo rechazado"),
                "source_module": resultado.metadata.get("modulo_origen"),
            }
        )
        if depuracion_habilitada:
            logging.debug(
                "USAR_SANITIZE_DEBUG %s",
                {
                    "module": alias_modulo,
                    "symbol": resultado.nombre,
                    "reason": resultado.codigo,
                },
            )

    metricas_rechazo_por_codigo: dict[str, int] = {}
    for conflicto in conflictos:
        codigo = str(conflicto.get("code") or "unknown")
        metricas_rechazo_por_codigo[codigo] = metricas_rechazo_por_codigo.get(codigo, 0) + 1
    if metricas_rechazo_por_codigo:
        logging.info(
            "USAR_SANITIZE_REJECTION_METRICS %s",
            {
                "module": alias_modulo,
                "rejection_metrics_by_codigo": metricas_rechazo_por_codigo,
            },
        )

    return simbolos_saneados, metadata_por_simbolo, conflictos
