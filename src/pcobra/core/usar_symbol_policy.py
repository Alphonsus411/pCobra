"""Política de saneamiento de símbolos para la instrucción ``usar``."""

from dataclasses import dataclass
from types import ModuleType
from typing import Any

NOMBRES_PUBLICOS_EQUIVALENTE_COBRA = frozenset(
    {
        "self",
        "append",
        "map",
        "filter",
        "unwrap",
        "expect",
        "keys",
        "values",
        "len",
    }
)
DUNDERS_BLOQUEADOS = frozenset(
    {"__builtins__", "__loader__", "__package__", "__spec__", "__name__"}
)
NOMBRES_BACKEND_INTERNOS = frozenset(
    {"sys", "os", "importlib", "pcobra", "cobra", "core"}
)
PREFIJOS_MODULOS_BACKEND_INTERNOS = (
    "sys",
    "os",
    "importlib",
    "pcobra",
    "cobra",
)


def _es_objeto_backend_no_exportable(simbolo: Any) -> bool:
    """Detecta objetos backend (módulos, tipos módulo, wrappers SDK/indirectos)."""
    if isinstance(simbolo, ModuleType):
        return True
    if isinstance(simbolo, type) and issubclass(simbolo, ModuleType):
        return True

    modulo_origen = getattr(simbolo, "__module__", "")
    if isinstance(modulo_origen, str) and modulo_origen.startswith(PREFIJOS_MODULOS_BACKEND_INTERNOS):
        return True

    referencia_envuelta = getattr(simbolo, "__wrapped__", None)
    if referencia_envuelta is not None and isinstance(referencia_envuelta, ModuleType):
        return True

    destino_sdk = getattr(simbolo, "_sdk", None)
    if isinstance(destino_sdk, ModuleType):
        return True

    return False


@dataclass(frozen=True)
class ResultadoSaneamientoSimboloUsar:
    nombre: str
    simbolo: object
    rechazado: bool
    codigo: str | None = None
    mensaje: str | None = None
    warning: bool = False


def _rechazar(nombre: str, simbolo: object, codigo: str, mensaje: str) -> ResultadoSaneamientoSimboloUsar:
    return ResultadoSaneamientoSimboloUsar(nombre, simbolo, True, codigo, mensaje)


def sanear_simbolo_para_usar(nombre: str, simbolo: object) -> ResultadoSaneamientoSimboloUsar:
    """Aplica la política de exportación de símbolos para ``usar``."""
    if nombre.startswith("_"):
        return _rechazar(
            nombre,
            simbolo,
            "private_prefix",
            "símbolos que inicien con '_' no son exportables",
        )

    if "__" in nombre:
        return _rechazar(
            nombre,
            simbolo,
            "dunder_pattern",
            "nombres con '__' no se permiten en usar",
        )

    if nombre in DUNDERS_BLOQUEADOS:
        return _rechazar(
            nombre,
            simbolo,
            "dunder_name",
            "dunders Python conocidos no se permiten en usar",
        )

    if _es_objeto_backend_no_exportable(simbolo):
        return _rechazar(
            nombre,
            simbolo,
            "backend_module_object",
            "objetos módulo/backend (incluye wrappers SDK e indirectos) no son exportables",
        )

    if nombre in NOMBRES_BACKEND_INTERNOS:
        return _rechazar(
            nombre,
            simbolo,
            "backend_internal_name",
            "nombre interno del backend bloqueado",
        )

    if nombre in NOMBRES_PUBLICOS_EQUIVALENTE_COBRA:
        return _rechazar(
            nombre,
            simbolo,
            "cobra_public_equivalent",
            "nombre público reservado por equivalente Cobra",
        )

    if not callable(simbolo) and not nombre.isupper():
        return _rechazar(
            nombre,
            simbolo,
            "non_callable_not_public_constant",
            "solo se permiten no-callables para constantes públicas explícitas",
        )

    if not callable(simbolo):
        return ResultadoSaneamientoSimboloUsar(
            nombre,
            simbolo,
            False,
            "public_constant",
            "constante pública explícita permitida",
            warning=True,
        )

    return ResultadoSaneamientoSimboloUsar(nombre, simbolo, False, "ok", "símbolo exportable")
