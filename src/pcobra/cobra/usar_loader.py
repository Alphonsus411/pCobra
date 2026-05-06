import importlib
import importlib.util
import re
from pathlib import Path
import sys

from pcobra.cobra.usar_policy import USAR_COBRA_ALLOWLIST, USAR_COBRA_PUBLIC_MODULES

# Módulos no canónicos conocidos que deben rechazarse de forma explícita.
_USAR_NON_CANONICAL_MODULES: frozenset[str] = frozenset({
    "numpy",
    "node-fetch",
    "serde",
    "holobit_sdk",
})

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
    "bindings",
    "transpiler",
)


def _rechazar_modulo_no_canonico(nombre: str) -> None:
    """Rechaza módulos backend/no-canónicos con error explícito para `usar`."""

    nombre_normalizado = (nombre or "").strip().lower()
    if nombre_normalizado in _USAR_NON_CANONICAL_MODULES:
        raise PermissionError(
            f"Importación no permitida en 'usar': '{nombre}'. "
            "Es un módulo backend/no canónico y no forma parte de la API pública. "
            f"Módulos permitidos: {', '.join(sorted(USAR_COBRA_ALLOWLIST))}."
        )

def validar_nombre_modulo_usar(nombre: str, *, require_allowlist: bool = True) -> str:
    """Valida nombre de `usar` y opcionalmente exige allowlist canónica."""

    _rechazar_modulo_no_canonico(nombre)
    nombre = nombre.strip()
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
