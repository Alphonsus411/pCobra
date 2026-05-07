"""Política de saneamiento de símbolos para la instrucción ``usar``."""

from dataclasses import dataclass
from types import ModuleType
from typing import Any

EQUIVALENCIAS_PROHIBIDAS_A_CANONICAS = {
    "self": "instancia",
    "append": "agregar",
    "map": "mapear",
    "filter": "filtrar",
    "unwrap": "obtener_o_error",
    "expect": "obtener_o_error",
    "keys": "claves",
    "values": "valores",
    "len": "longitud",
}

NOMBRES_PROHIBIDOS_EXPLICITOS = frozenset(EQUIVALENCIAS_PROHIBIDAS_A_CANONICAS)
DUNDERS_BLOQUEADOS = frozenset(
    {"__builtins__", "__loader__", "__package__", "__spec__", "__name__"}
)
NOMBRES_CONSTANTES_PUBLICAS_CANONICAS = frozenset(
    {
        "PI",
        "E",
        "TAU",
        "INF",
        "NAN",
    }
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


def _mensaje_nombre_prohibido(nombre: str) -> str:
    recomendado = EQUIVALENCIAS_PROHIBIDAS_A_CANONICAS.get(nombre)
    if recomendado:
        return (
            f"nombre '{nombre}' no permitido por política de usar. "
            f"Usa el nombre Cobra canónico '{recomendado}'."
        )
    return "nombre prohibido por política explícita de usar"


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

    if nombre in NOMBRES_PROHIBIDOS_EXPLICITOS:
        return _rechazar(
            nombre,
            simbolo,
            "explicit_forbidden_name",
            _mensaje_nombre_prohibido(nombre),
        )

    if not callable(simbolo) and nombre not in NOMBRES_CONSTANTES_PUBLICAS_CANONICAS:
        return _rechazar(
            nombre,
            simbolo,
            "non_callable_not_canonical_public_constant",
            "solo se permiten no-callables para constantes públicas explícitas y canónicas",
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


def sanear_exportables_para_usar(
    simbolos: list[tuple[str, object]],
) -> tuple[list[tuple[str, object]], list[ResultadoSaneamientoSimboloUsar], list[ResultadoSaneamientoSimboloUsar]]:
    """Sanea una lista de símbolos candidatos para ``usar`` de forma uniforme."""

    permitidos: list[tuple[str, object]] = []
    rechazos: list[ResultadoSaneamientoSimboloUsar] = []
    warnings: list[ResultadoSaneamientoSimboloUsar] = []
    for nombre, simbolo in simbolos:
        resultado = sanear_simbolo_para_usar(nombre, simbolo)
        if resultado.rechazado:
            rechazos.append(resultado)
            continue
        if resultado.warning:
            warnings.append(resultado)
        permitidos.append((nombre, simbolo))
    return permitidos, rechazos, warnings
