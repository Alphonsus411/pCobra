"""Política de saneamiento de símbolos para la instrucción ``usar``."""

from dataclasses import dataclass
from types import ModuleType

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


@dataclass(frozen=True)
class ResultadoSaneamientoSimboloUsar:
    nombre: str
    simbolo: object
    rechazado: bool
    codigo: str | None = None
    mensaje: str | None = None
    warning: bool = False


def sanear_simbolo_para_usar(nombre: str, simbolo: object) -> ResultadoSaneamientoSimboloUsar:
    """Aplica la política de exportación de símbolos para ``usar``."""
    if isinstance(simbolo, ModuleType):
        return ResultadoSaneamientoSimboloUsar(
            nombre,
            simbolo,
            True,
            "backend_module_object",
            "objetos módulo/paquete no son exportables",
        )
    if "__" in nombre or nombre in DUNDERS_BLOQUEADOS:
        return ResultadoSaneamientoSimboloUsar(
            nombre,
            simbolo,
            True,
            "dunder_name",
            "dunders Python no se permiten en usar",
        )
    if nombre.startswith("_"):
        return ResultadoSaneamientoSimboloUsar(
            nombre,
            simbolo,
            True,
            "private_prefix",
            "símbolos que inicien con '_' no son exportables",
        )
    if nombre in NOMBRES_BACKEND_INTERNOS:
        return ResultadoSaneamientoSimboloUsar(
            nombre,
            simbolo,
            True,
            "backend_internal_name",
            "nombre interno del backend bloqueado",
        )
    if nombre in NOMBRES_PUBLICOS_EQUIVALENTE_COBRA:
        return ResultadoSaneamientoSimboloUsar(
            nombre,
            simbolo,
            True,
            "cobra_public_equivalent",
            "nombre público reservado por equivalente Cobra",
        )
    if not callable(simbolo) and not nombre.isupper():
        return ResultadoSaneamientoSimboloUsar(
            nombre,
            simbolo,
            True,
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
    return ResultadoSaneamientoSimboloUsar(nombre, simbolo, False)
