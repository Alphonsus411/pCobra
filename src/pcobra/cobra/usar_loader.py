import importlib
import importlib.util
import logging
import re
from pathlib import Path
import sys
from typing import Any

from pcobra.cobra.usar_policy import (
    CANONICAL_MODULE_SURFACE_CONTRACTS,
    USAR_BACKEND_BLOCKLIST,
    USAR_COBRA_ALLOWLIST,
    USAR_COBRA_PUBLIC_MODULES,
    USAR_RUNTIME_EXPORT_OVERRIDES,
)
from pcobra.core.usar_symbol_policy import (
    depuracion_saneamiento_usar_habilitada,
    sanear_exportables_para_usar,
)

# Regex estricta para mantener la sintaxis `usar "modulo"` acotada a identificadores simples.
_VALID_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")

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
            f"Módulos permitidos: {', '.join(sorted(USAR_COBRA_ALLOWLIST))}."
        )

    if any(
        nombre_normalizado == prefijo or nombre_normalizado.startswith(f"{prefijo}_")
        for prefijo in _BACKEND_PREFIXES
    ):
        raise PermissionError(
            f"Importación no permitida en 'usar': '{nombre}'. "
            "Es un módulo backend/no canónico y no forma parte de la API pública. "
            f"Módulos permitidos: {', '.join(sorted(USAR_COBRA_ALLOWLIST))}."
        )

def validar_nombre_modulo_usar(nombre: str, *, require_allowlist: bool = True) -> str:
    """Valida nombre de `usar` y opcionalmente exige allowlist canónica."""

    _rechazar_modulo_no_canonico(nombre)
    nombre = normalizar_nombre_usar(nombre)
    if not nombre:
        raise ValueError("Nombre de módulo vacío en 'usar'.")

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

    if require_allowlist and nombre not in USAR_COBRA_ALLOWLIST:
        raise PermissionError(
            f"Importación no permitida en 'usar': '{nombre}'. "
            f"Módulos permitidos: {', '.join(sorted(USAR_COBRA_ALLOWLIST))}."
        )

    return nombre


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


def obtener_modulo_cobra_oficial(nombre: str):
    """Carga módulos oficiales de Cobra solo desde ``corelibs`` o ``standard_library``."""

    nombre = validar_nombre_modulo_usar(nombre, require_allowlist=True)
    base = Path(__file__).resolve()

    for parent in base.parents:
        corelibs = parent / "corelibs"
        if corelibs.exists():
            modulo = _cargar_modulo_local_desde_directorio(nombre, corelibs)
            if modulo is not None:
                return modulo
            break

    for parent in base.parents:
        stdlib = parent / "standard_library"
        if stdlib.exists():
            modulo = _cargar_modulo_local_desde_directorio(nombre, stdlib)
            if modulo is not None:
                return modulo
            break

    raise ModuleNotFoundError(
        f"Módulo oficial Cobra '{nombre}' no encontrado en corelibs/standard_library"
    )


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
    mapa_limpio = {nombre: simbolo for nombre, simbolo in simbolos_saneados}

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

    return mapa_limpio, conflictos
