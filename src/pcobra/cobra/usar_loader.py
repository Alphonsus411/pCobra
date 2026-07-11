import importlib
import importlib.util
import logging
import os
import re
import shlex
from pathlib import Path
import subprocess
import sys
import tomllib as tomli
from typing import Any

from pcobra.cobra.imports import resolver as imports_resolver
from pcobra.cobra.imports.resolver import ImportResolutionError
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
_VALID_NAME_RE = re.compile(r"^[a-z][a-z0-9_.]*$")


# Segmentos seguros para módulos de proyecto: ruta lógica punteada, no ruta del sistema.
_VALID_PROJECT_MODULE_SEGMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_PROJECT_MODULE_FORBIDDEN_CHARS = frozenset('/\\@$%*?"\'<>|;`!()[]{}=+,')
_USAR_PROJECT_MODULE_CACHE: dict[Path, dict[str, Any]] = {}
_USAR_PROJECT_LOADING_STACK: list[Path] = []
_IMPORT_CO_AST_CACHE: dict[Path, list[Any]] = {} # Nueva caché para ASTs de .co

# Compatibilidad con la API histórica de ``usar_loader``.  La política
# canónica vive en ``usar_policy``, pero algunas integraciones y pruebas siguen
# extendiendo esta lista blanca para módulos Python externos controlados.
USAR_WHITELIST: dict[str, str] = {
    "numpy": "numpy",
    "agix": "agix",
    **{modulo: modulo for modulo in USAR_COBRA_PUBLIC_MODULES},
}

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

    partes_mensaje_error_no_canonico = [
        f"Importación no permitida en 'usar': '{nombre}'.",
        "Es un módulo backend/no canónico y no forma parte de la API pública.",
    ]
    detalle_repl_estricto = (
        "módulo externo no permitido en REPL estricto (solo alias oficiales Cobra)."
    )
    if detalle_repl_estricto:
        partes_mensaje_error_no_canonico.append(detalle_repl_estricto)
    if USAR_COBRA_PUBLIC_MODULES:
        modulos_permitidos = ", ".join(USAR_COBRA_PUBLIC_MODULES)
        partes_mensaje_error_no_canonico.append(
            f"Módulos permitidos: {modulos_permitidos}."
        )
    mensaje_error_no_canonico = " ".join(partes_mensaje_error_no_canonico)

    if nombre_normalizado in blocklist_normalizada or nombre_normalizado in equivalentes_normalizados:
        raise PermissionError(mensaje_error_no_canonico)

    if any(
        nombre_normalizado == prefijo or nombre_normalizado.startswith(f"{prefijo}_")
        for prefijo in _BACKEND_PREFIXES
    ):
        raise PermissionError(mensaje_error_no_canonico)

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

    # `usar` de proyecto acepta únicamente rutas lógicas punteadas, nunca rutas
    # del sistema. Bloqueamos separadores POSIX/Windows, traversal, rutas
    # absolutas y cualquier forma de unidad Windows antes de resolver.
    if any(sep in nombre_raw for sep in ("/", "\\")):
        raise ValueError(
            f"Nombre de módulo de proyecto inválido: '{nombre_raw}' no debe contener separadores de ruta."
        )
    if ".." in nombre_raw:
        raise ValueError(
            f"Nombre de módulo de proyecto inválido: '{nombre_raw}' contiene traversal."
        )
    if os.path.isabs(nombre_raw) or re.match(r"^[A-Za-z]:", nombre_raw):
        raise ValueError(
            f"Nombre de módulo de proyecto inválido: '{nombre_raw}' parece una ruta absoluta o unidad Windows."
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

    root_canonico = canonicalizar_ruta_usar_proyecto(root)
    ruta_canonica = canonicalizar_ruta_usar_proyecto(ruta)
    try:
        common = os.path.commonpath((str(root_canonico), str(ruta_canonica)))
    except ValueError as exc:
        raise ValueError("Ruta de módulo de proyecto fuera de la raíz autorizada.") from exc

    if common != str(root_canonico):
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

    ruta_directa = root_resuelto.joinpath(
        *validar_nombre_modulo_cobra_proyecto(nombre)
    ).with_suffix(".co")
    if ruta_directa.exists():
        ruta_directa = canonicalizar_ruta_usar_proyecto(ruta_directa)
        _verificar_path_dentro_de_root(ruta_directa, root_resuelto)
        return ruta_directa

    # Compatibilidad legacy: el resolver histórico sólo puede actuar como
    # fallback cuando haya sido sustituido explícitamente por un caller/test.
    # La ruta principal y estable para `usar utilidades.fechas` es siempre:
    # `project_root / "utilidades" / "fechas.co"`.
    resolver_cls = imports_resolver.CobraImportResolver
    if getattr(resolver_cls, "__module__", "") == "pcobra.cobra.imports.resolver":
        raise FileNotFoundError(f"Módulo no encontrado: {nombre}")

    try:
        resolution = resolver_cls(
            project_root=root_resuelto,
            collision_policy="warn",
        ).resolve(nombre)
    except ImportResolutionError as exc:
        if exc.code == "IMP-PROJECT-PATH-001":
            raise ValueError("Ruta de módulo de proyecto fuera de la raíz autorizada.") from exc
        raise FileNotFoundError(f"Módulo no encontrado: {nombre}") from exc

    if resolution.source != "project" or not resolution.file_path:
        raise FileNotFoundError(f"Módulo no encontrado: {nombre}")

    ruta_resuelta = canonicalizar_ruta_usar_proyecto(resolution.file_path)
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


def obtener_cache_modulos_cobra_proyecto() -> dict[Path, dict[str, Any]]:
    """Expone la caché compartida de módulos de proyecto para el intérprete."""

    return _USAR_PROJECT_MODULE_CACHE


def obtener_pila_carga_modulos_cobra_proyecto() -> list[Path]:
    """Expone la pila compartida de carga para detectar ciclos entre entrypoints."""

    return _USAR_PROJECT_LOADING_STACK


def obtener_cache_ast_import_co() -> dict[Path, list[Any]]:
    """Expone la caché compartida de ASTs de módulos .co para el transpilador."""
    return _IMPORT_CO_AST_CACHE


def _formatear_ruta_ciclo_modulo(ruta: Path, project_root: Path | None) -> str:
    """Formatea una ruta de ciclo de forma estable y legible."""

    try:
        ruta_canonica = canonicalizar_ruta_usar_proyecto(ruta)
    except (OSError, RuntimeError, ValueError):
        return ruta.name or str(ruta)

    if project_root is not None:
        try:
            raiz_canonica = canonicalizar_ruta_usar_proyecto(project_root)
            return ruta_canonica.relative_to(raiz_canonica).as_posix()
        except (OSError, RuntimeError, ValueError):
            pass

    return str(ruta_canonica) if str(ruta_canonica) else (ruta.name or str(ruta))


def formatear_ciclo_modulos_cobra_proyecto(
    ruta_modulo: Path,
    *,
    project_root: Path | None = None,
    loading_stack: list[Path] | None = None,
) -> str:
    """Construye una cadena clara del ciclo usando rutas relativas si es posible."""

    ruta_canonica = canonicalizar_ruta_usar_proyecto(ruta_modulo)
    pila_origen = loading_stack if loading_stack is not None else _USAR_PROJECT_LOADING_STACK
    pila: list[Path] = []
    for ruta in pila_origen:
        ruta_pila = canonicalizar_ruta_usar_proyecto(ruta)
        if not pila or pila[-1] != ruta_pila:
            pila.append(ruta_pila)

    ciclo = [*pila, ruta_canonica]
    try:
        inicio = ciclo.index(ruta_canonica)
    except ValueError:
        inicio = max(0, len(ciclo) - 1)
    ciclo_detectado = ciclo[inicio:]
    if len(ciclo_detectado) > 50:
        ciclo_detectado = [*ciclo_detectado[:49], ruta_canonica]
    return " -> ".join(
        _formatear_ruta_ciclo_modulo(ruta, project_root) for ruta in ciclo_detectado
    )


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


def _obtener_modulo_cobra_oficial_compat(nombre: str):
    """Obtiene un módulo oficial respetando wrappers legacy parcheados."""

    wrapper = sys.modules.get("pcobra.core.usar_loader") or sys.modules.get("core.usar_loader")
    wrapper_oficial = getattr(wrapper, "obtener_modulo_cobra_oficial", None)
    if (
        wrapper_oficial is not None
        and getattr(wrapper_oficial, "__module__", "") != "pcobra.core.usar_loader"
    ):
        modulo = wrapper_oficial(nombre)
        return modulo
    else:
        modulo = obtener_modulo_cobra_oficial(nombre)

    rel_path = REPL_COBRA_MODULE_INTERNAL_PATH_MAP.get(nombre)
    if rel_path:
        ruta_oficial = (Path(__file__).resolve().parents[3] / rel_path).resolve()
        modulo_file = getattr(modulo, "__file__", None)
        if not modulo_file or Path(modulo_file).resolve() != ruta_oficial:
            raise PermissionError(
                "usar_error[modulo_no_permitido]: módulo externo no permitido en REPL estricto "
                "(solo alias oficiales Cobra)"
            )
    return modulo


def _repo_root_desde_loader() -> Path:
    """Busca la raíz del proyecto/instalación partiendo de este archivo."""

    for candidato in Path(__file__).resolve().parents:
        if (candidato / "cobra.toml").exists() or (candidato / "pyproject.toml").exists():
            return candidato
    return Path(__file__).resolve().parents[3]


def cargar_lista_blanca() -> dict[str, str]:
    """Carga paquetes permitidos legacy desde ``cobra.toml`` si existe.

    Mantiene los valores hardcoded históricos cuando no hay configuración de
    proyecto, y añade entradas declaradas como ``[usar].permitidos`` cuando la
    raíz contiene ``cobra.toml``.
    """

    USAR_WHITELIST.clear()
    USAR_WHITELIST.update(
        {
            "numpy": "numpy",
            "agix": "agix",
            **{modulo: modulo for modulo in USAR_COBRA_PUBLIC_MODULES},
        }
    )

    config = _repo_root_desde_loader() / "cobra.toml"
    if not config.exists():
        return USAR_WHITELIST

    datos = tomli.loads(config.read_text(encoding="utf-8"))
    permitidos = datos.get("usar", {}).get("permitidos", [])
    for spec in permitidos:
        if not isinstance(spec, str) or not spec.strip():
            continue
        spec_limpio = spec.strip()
        nombre = re.split(r"[<>=!~\s]", spec_limpio, maxsplit=1)[0]
        if nombre:
            USAR_WHITELIST[nombre] = spec_limpio
    return USAR_WHITELIST


def _argumentos_pip_desde_spec(spec: str) -> list[str]:
    """Convierte una spec permitida en argumentos para ``pip install``."""

    if os.environ.get("COBRA_USAR_INSTALL_UNSAFE_SPECS") == "1":
        return shlex.split(spec)
    if re.search(r"\s", spec):
        raise RuntimeError(
            "Spec de instalación no segura en 'usar'; habilita "
            "COBRA_USAR_INSTALL_UNSAFE_SPECS=1 para flags explícitos."
        )
    return [spec]


def obtener_modulo(nombre: str, *, permitir_instalacion: bool = True):
    """Resuelve módulos de `usar` contra Cobra canónico o allowlist legacy."""

    nombre = validar_nombre_modulo_usar(nombre, require_allowlist=False)
    if nombre not in USAR_WHITELIST:
        raise PermissionError(f"Paquete no permitido en 'usar': '{nombre}'.")

    resolver_cls = imports_resolver.CobraImportResolver
    resolver_parcheado = getattr(resolver_cls, "__module__", "") != "pcobra.cobra.imports.resolver"
    if nombre in USAR_COBRA_PUBLIC_MODULES:
        try:
            return _obtener_modulo_cobra_oficial_compat(nombre)
        except ModuleNotFoundError as oficial_exc:
            raise ImportError(
                f"No se pudo resolver el módulo Cobra permitido '{nombre}' en runtime."
            ) from oficial_exc

    if nombre not in USAR_COBRA_PUBLIC_MODULES and resolver_parcheado:
        _resolution, modulo = resolver_cls().load_module(nombre, fallback_backend="python")
        return modulo

    try:
        return importlib.import_module(nombre)
    except ModuleNotFoundError as import_exc:
        try:
            _resolution, modulo = resolver_cls().load_module(nombre, fallback_backend="python")
            return modulo
        except Exception:
            if not permitir_instalacion or os.environ.get("COBRA_USAR_INSTALL") != "1":
                raise RuntimeError(
                    f"Módulo '{nombre}' no instalado y la instalación automática está deshabilitada."
                ) from import_exc

            spec = USAR_WHITELIST[nombre]
            subprocess.run(
                [sys.executable, "-m", "pip", "install", *_argumentos_pip_desde_spec(spec)],
                check=True,
            )
            return importlib.import_module(nombre)


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
) -> dict[str, Any]:
    """Carga un módulo Cobra de proyecto usando resolución canónica y cache."""

    from pcobra.core.environment import Environment
    from pcobra.core.import_utils import cargar_ast_modulo
    from pcobra.core.interpreter import InterpretadorCobra
    from pcobra.core.ast_nodes import NodoExport, NodoUsar

    root_canonico = canonicalizar_ruta_usar_proyecto(project_root)
    current_canonico = (
        canonicalizar_ruta_usar_proyecto(current_file) if current_file else None
    )
    if current_canonico is not None:
        _verificar_path_dentro_de_root(current_canonico, root_canonico)

    ruta_modulo = resolver_ruta_canonica_modulo_cobra_proyecto(
        nombre,
        project_root=root_canonico,
        current_file=current_canonico,
    )
    _verificar_path_dentro_de_root(ruta_modulo, root_canonico)

    if ruta_modulo in _USAR_PROJECT_MODULE_CACHE:
        return _USAR_PROJECT_MODULE_CACHE[ruta_modulo]

    if ruta_modulo in _USAR_PROJECT_LOADING_STACK:
        cadena = formatear_ciclo_modulos_cobra_proyecto(
            ruta_modulo, project_root=root_canonico
        )
        raise ImportError(f"Ciclo de módulos detectado en usar: {cadena}")

    _USAR_PROJECT_LOADING_STACK.append(ruta_modulo)
    interpretador = None
    try:
        try:
            ast = cargar_ast_modulo(
                str(ruta_modulo),
                modules_path=str(root_canonico),
                whitelist={root_canonico},
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Módulo no encontrado: {nombre}") from exc

        interpretador = InterpretadorCobra(
            safe_mode=False, main_file=current_canonico or ruta_modulo
        )
        interpretador._project_root = root_canonico
        interpretador._main_file = (
            current_canonico if current_canonico else ruta_modulo
        )
        interpretador._current_module_stack.append(ruta_modulo)
        interpretador.contextos.append(Environment(parent=interpretador.contextos[-1]))
        interpretador.mem_contextos.append({})
        for subnodo in ast:
            if isinstance(subnodo, NodoExport):
                continue
            if isinstance(subnodo, NodoUsar) or subnodo.__class__.__name__ == "NodoUsar":
                modulo_hijo = str(subnodo.modulo).strip().strip('\"\'')
                ruta_hijo = resolver_ruta_canonica_modulo_cobra_proyecto(
                    modulo_hijo,
                    project_root=root_canonico,
                    current_file=ruta_modulo,
                )
                _verificar_path_dentro_de_root(ruta_hijo, root_canonico)
                if ruta_hijo in _USAR_PROJECT_LOADING_STACK:
                    cadena = formatear_ciclo_modulos_cobra_proyecto(
                        ruta_hijo, project_root=root_canonico
                    )
                    raise ImportError(f"Ciclo de módulos detectado en usar: {cadena}")
            interpretador.ejecutar_nodo(subnodo)
        exports = _extraer_exports_modulo_cobra_proyecto(
            ast,
            interpretador.contextos[-1],
            ruta_modulo=ruta_modulo,
        )
        _USAR_PROJECT_MODULE_CACHE[ruta_modulo] = _construir_exports_usar(
            list(exports["simbolos"]),
            {
                nombre: dict(metadata)
                for nombre, metadata in exports["metadata"].items()
            },
        )
        return _USAR_PROJECT_MODULE_CACHE[ruta_modulo]
    finally:
        if interpretador is not None:
            memoria_local = interpretador.mem_contextos.pop()
            for idx, tam in memoria_local.values():
                interpretador.liberar_memoria(idx, tam)
            interpretador.contextos.pop()
            interpretador._current_module_stack.pop()
        if _USAR_PROJECT_LOADING_STACK and _USAR_PROJECT_LOADING_STACK[-1] == ruta_modulo:
            _USAR_PROJECT_LOADING_STACK.pop()
        elif ruta_modulo in _USAR_PROJECT_LOADING_STACK:
            _USAR_PROJECT_LOADING_STACK.remove(ruta_modulo)


def usar_modulo(
    nombre: str,
    *,
    project_root: str | Path | None = None,
    current_file: str | Path | None = None,
) -> dict[str, Any]:
    """API única para resolver ``usar`` en runtime y transpilación Python.

    - Los módulos oficiales preservan ``obtener_modulo`` y devuelven sus
      símbolos públicos saneados.
    - Los módulos Cobra de proyecto (``foo.bar`` -> ``foo/bar.co``) usan la
      misma resolución canónica por ruta y una cache global por archivo.
    """

    nombre_raw = nombre.strip()
    if not nombre_raw:
        raise ValueError("Nombre de módulo vacío en 'usar'.")

    # 1. Intentar cargar como módulo oficial Cobra
    try:
        nombre_validado_oficial = validar_nombre_modulo_usar(nombre_raw, require_allowlist=True)
        modulo = obtener_modulo(nombre_validado_oficial)
        simbolos_saneados, metadata_por_simbolo, conflictos = sanitizar_exports_publicos(
            modulo,
            normalizar_nombre_usar(nombre_validado_oficial),
        )
        if conflictos:
            logging.debug(
                "USAR sanitize conflicts en API única module=%s conflicts=%s",
                nombre_validado_oficial,
                conflictos,
            )
        if not simbolos_saneados:
            raise ImportError(f"No se encontraron símbolos exportables para usar '{nombre_validado_oficial}'.")
        return _construir_exports_usar(simbolos_saneados, metadata_por_simbolo)
    except PermissionError as permiso_exc:
        try:
            wrapper = sys.modules.get("pcobra.core.usar_loader") or sys.modules.get("core.usar_loader")
            wrapper_obtener = getattr(wrapper, "obtener_modulo", None)
            if not (
                wrapper_obtener is not None
                and getattr(wrapper_obtener, "__module__", "") != "pcobra.core.usar_loader"
            ):
                raise permiso_exc
            modulo = wrapper_obtener(nombre_raw)
            simbolos_saneados, metadata_por_simbolo, conflictos = sanitizar_exports_publicos(
                modulo,
                normalizar_nombre_usar(nombre_raw),
            )
            if conflictos:
                logging.debug(
                    "USAR sanitize conflicts en API única legacy module=%s conflicts=%s",
                    nombre_raw,
                    conflictos,
                )
            if not simbolos_saneados:
                raise ImportError(f"No se encontraron símbolos exportables para usar '{nombre_raw}'.")
            return _construir_exports_usar(simbolos_saneados, metadata_por_simbolo)
        except Exception:
            raise permiso_exc
    except (ModuleNotFoundError, ValueError):
        # Si no es un módulo oficial o no está permitido, intentar como módulo de proyecto
        # Si es un ValueError, significa que el nombre no es válido para un módulo oficial,
        # pero podría serlo para un módulo de proyecto (ej. contiene puntos).
        pass

    # 2. Intentar cargar como módulo de proyecto
    try:
        segmentos_proyecto = validar_nombre_modulo_cobra_proyecto(nombre_raw)
        nombre_validado_proyecto = ".".join(segmentos_proyecto)

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
                nombre_validado_proyecto,
                project_root=root,
                current_file=current,
            )
            return exports
        except ValueError:
            raise
        except FileNotFoundError as exc:
            ruta_buscada = root.joinpath(
                *nombre_validado_proyecto.split(".")
            ).with_suffix(".co")
            raise FileNotFoundError(
                f"Módulo de proyecto no encontrado: {nombre_validado_proyecto}. Ruta buscada: {ruta_buscada}"
            ) from exc
    except ValueError as e:
        # Si tampoco es un módulo de proyecto válido, entonces el nombre es inválido.
        raise ValueError(f"Nombre de módulo inválido en 'usar': '{nombre_raw}'.") from e
    except FileNotFoundError as e:
        raise e


def _registrar_conflicto_saneamiento_usar(
    conflictos: list[dict[str, Any]],
    conflicto: dict[str, Any],
    *,
    depuracion_habilitada: bool,
) -> None:
    """Registra un conflicto de saneamiento y emite trazas útiles cuando aplica."""

    conflictos.append(conflicto)
    debe_trazar = depuracion_habilitada or (
        conflicto.get("module") == "datos" and conflicto.get("symbol") == "filtrar"
    )
    if debe_trazar:
        logging.debug(
            "USAR_SANITIZE_DEBUG %s",
            {
                "module": conflicto.get("module"),
                "symbol": conflicto.get("symbol"),
                "reason": conflicto.get("code"),
                "message": conflicto.get("message"),
            },
        )


def sanitizar_exports_publicos(modulo: object, alias_modulo: str) -> tuple[list[tuple[str, Any]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
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
            _registrar_conflicto_saneamiento_usar(
                conflictos,
                {
                    "module": alias_modulo,
                    "symbol": repr(nombre),
                    "code": "invalid_export_name_type",
                    "message": "nombre de export no es string",
                },
                depuracion_habilitada=depuracion_habilitada,
            )
            continue
        if nombre in vistos:
            _registrar_conflicto_saneamiento_usar(
                conflictos,
                {
                    "module": alias_modulo,
                    "symbol": nombre,
                    "code": "duplicate_export_name",
                    "message": "nombre exportado repetido en __all__/candidatos",
                },
                depuracion_habilitada=depuracion_habilitada,
            )
            continue
        if not hasattr(modulo, nombre):
            _registrar_conflicto_saneamiento_usar(
                conflictos,
                {
                    "module": alias_modulo,
                    "symbol": nombre,
                    "code": "missing_export_attr",
                    "message": "el nombre exportado no existe en el módulo",
                },
                depuracion_habilitada=depuracion_habilitada,
            )
            continue
        if api_publica_modulo and nombre not in api_publica_modulo:
            _registrar_conflicto_saneamiento_usar(
                conflictos,
                {
                    "module": alias_modulo,
                    "symbol": nombre,
                    "code": "outside_public_api",
                    "message": "símbolo descartado por no pertenecer a la API pública canónica",
                },
                depuracion_habilitada=depuracion_habilitada,
            )
            continue
        vistos.add(nombre)
        simbolos_brutos.append((nombre, getattr(modulo, nombre)))

    simbolos_saneados, clasificacion, warnings = sanear_exportables_para_usar(
        simbolos_brutos,
        modulo_origen=alias_modulo,
    )
    metadata_por_simbolo: dict[str, dict[str, Any]] = {}
    simbolos_con_metadata_valida: list[tuple[str, Any]] = []
    for nombre, simbolo in simbolos_saneados:
        try:
            metadata_por_simbolo[nombre] = build_and_validate_usar_symbol_metadata(
                module_name=alias_modulo,
                symbol_name=nombre,
                callable_obj=simbolo,
            )
        except ValueError as exc:
            _registrar_conflicto_saneamiento_usar(
                conflictos,
                {
                    "module": alias_modulo,
                    "symbol": nombre,
                    "code": "metadata_conflict",
                    "message": f"metadata de símbolo inválida o inconsistente: {exc}",
                },
                depuracion_habilitada=depuracion_habilitada,
            )
            continue
        simbolos_con_metadata_valida.append((nombre, simbolo))
    simbolos_saneados = simbolos_con_metadata_valida

    for resultado in [*clasificacion.rechazos_duros, *warnings]:
        _registrar_conflicto_saneamiento_usar(
            conflictos,
            {
                "module": alias_modulo,
                "symbol": resultado.nombre,
                "code": resultado.codigo or ("warning" if resultado.warning else "rejected"),
                "message": resultado.mensaje or ("warning de saneamiento" if resultado.warning else "símbolo rechazado"),
                "source_module": resultado.metadata.get("modulo_origen"),
            },
            depuracion_habilitada=depuracion_habilitada,
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
