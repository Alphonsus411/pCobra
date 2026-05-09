"""Política de saneamiento de símbolos para la instrucción ``usar``."""

from dataclasses import dataclass, field
import os
from types import ModuleType
from typing import Any

EQUIVALENCIAS_PROHIBIDAS_A_CANONICAS = {
    "self": "instancia",
    "append": "agregar",
    "map": "mapear",
    "filter": "filtrar",
    "reduce": "reducir",
    "unwrap": "obtener_o_error",
    "expect": "obtener_o_error",
    "keys": "claves",
    "values": "valores",
    "len": "longitud",
    "length": "longitud",
    "lower": "minusculas",
    "upper": "mayusculas",
    "items": "elementos",
    "get": "obtener",
    "setdefault": "definir_por_defecto",
    "update": "actualizar",
    "pop": "extraer",
    "clear": "limpiar",
    "copy": "copiar",
    "split": "separar",
    "join": "unir",
    "strip": "recortar",
    "replace": "reemplazar",
    "startswith": "inicia_con",
    "endswith": "termina_con",
    "Holobit": "crear_holobit",
    "holobit_sdk": "crear_holobit",
}

NOMBRES_PROHIBIDOS_EXPLICITOS = frozenset(EQUIVALENCIAS_PROHIBIDAS_A_CANONICAS)
DUNDERS_BLOQUEADOS = frozenset(
    {"__builtins__", "__loader__", "__package__", "__spec__", "__name__"}
)
NOMBRES_CONSTANTES_PUBLICAS_CANONICAS = frozenset({"PI", "E", "TAU", "INF", "NAN"})
NOMBRES_BACKEND_INTERNOS = frozenset(
    {"sys", "os", "importlib", "pcobra", "cobra", "core"}
)
PREFIJOS_MODULOS_BACKEND_INTERNOS = (
    "sys",
    "os",
    "importlib",
    "pcobra",
    "cobra",
    "holobit_sdk",
    "wrapped",
)


@dataclass(frozen=True)
class PoliticaSaneamientoUsar:
    """Configuración de saneamiento para ``usar``.

    En módulos Cobra-facing puede habilitarse validación estricta para
    rechazar cualquier nombre no canónico (en vez de permitirlo con warning).
    """

    validar_nombre_canonico_espanol_en_cobra_facing: bool = False


@dataclass(frozen=True)
class ResultadoSaneamientoSimboloUsar:
    nombre: str
    simbolo: object
    rechazado: bool
    codigo: str | None = None
    mensaje: str | None = None
    warning: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ClasificacionSaneamientoUsar:
    rechazos_duros: list[ResultadoSaneamientoSimboloUsar]
    warnings_transicion: list[ResultadoSaneamientoSimboloUsar]


def _contiene_rastro_sdk_en_texto(texto: str) -> bool:
    normalizado = texto.strip().lower()
    return "holobit_sdk" in normalizado or "sdk" in normalizado or "wrapped" in normalizado


def _es_objeto_backend_no_exportable(simbolo: Any) -> bool:
    """Detecta objetos backend (módulos, tipos módulo, wrappers SDK/indirectos)."""
    if isinstance(simbolo, ModuleType):
        return True
    if isinstance(simbolo, type) and issubclass(simbolo, ModuleType):
        return True

    modulo_origen = getattr(simbolo, "__module__", "")
    if isinstance(modulo_origen, str):
        if modulo_origen.startswith(PREFIJOS_MODULOS_BACKEND_INTERNOS) or _contiene_rastro_sdk_en_texto(modulo_origen):
            return True

    referencia_envuelta = getattr(simbolo, "__wrapped__", None)
    if referencia_envuelta is not None and _contiene_rastro_sdk_en_texto(type(referencia_envuelta).__module__):
        return True
    if referencia_envuelta is not None and isinstance(referencia_envuelta, ModuleType):
        return True

    destino_sdk = getattr(simbolo, "_sdk", None)
    if isinstance(destino_sdk, ModuleType):
        return True

    return False


def _rechazar(nombre: str, simbolo: object, codigo: str, mensaje: str, metadata: dict[str, object]) -> ResultadoSaneamientoSimboloUsar:
    return ResultadoSaneamientoSimboloUsar(nombre, simbolo, True, codigo, mensaje, metadata=metadata)


def _mensaje_nombre_prohibido(nombre: str) -> str:
    recomendado = EQUIVALENCIAS_PROHIBIDAS_A_CANONICAS.get(nombre)
    if recomendado:
        return (
            f"nombre '{nombre}' no permitido por política de usar. "
            f"Usa el nombre Cobra canónico '{recomendado}'."
        )
    return "nombre prohibido por política explícita de usar"


def _parece_nombre_canonico_espanol(nombre: str) -> bool:
    return nombre.isidentifier() and nombre.lower() == nombre and "_" in nombre


def depuracion_saneamiento_usar_habilitada() -> bool:
    """Indica si la depuración opcional de saneamiento de `usar` está activa."""
    return os.getenv("PCOBRA_USAR_DEBUG_SANITIZE", "").strip().lower() in {
        "1",
        "true",
        "si",
        "yes",
        "on",
    }


def sanear_simbolo_para_usar(
    nombre: str,
    simbolo: object,
    *,
    politica: PoliticaSaneamientoUsar | None = None,
    modulo_origen: str | None = None,
    modulo_cobra_facing: bool = False,
) -> ResultadoSaneamientoSimboloUsar:
    """Aplica la política de exportación de símbolos para ``usar``."""
    politica_efectiva = politica or PoliticaSaneamientoUsar()
    metadata = {"modulo_origen": modulo_origen, "modulo_cobra_facing": modulo_cobra_facing}

    if nombre == "holobit_sdk":
        return _rechazar(nombre, simbolo, "cobra_public_equivalent", _mensaje_nombre_prohibido(nombre), metadata)

    if nombre in DUNDERS_BLOQUEADOS:
        return _rechazar(nombre, simbolo, "dunder_name", "dunders Python conocidos no se permiten en usar", metadata)

    if nombre.startswith("_"):
        return _rechazar(nombre, simbolo, "private_prefix", "símbolos que inicien con '_' no son exportables", metadata)

    if "__" in nombre:
        return _rechazar(nombre, simbolo, "dunder_pattern", "nombres con '__' no se permiten en usar", metadata)

    if _es_objeto_backend_no_exportable(simbolo):
        return _rechazar(nombre, simbolo, "backend_module_object", "objetos módulo/backend (incluye wrappers SDK e indirectos) no son exportables", metadata)

    if nombre in NOMBRES_BACKEND_INTERNOS:
        return _rechazar(nombre, simbolo, "backend_internal_name", "nombre interno del backend bloqueado", metadata)

    if nombre in NOMBRES_PROHIBIDOS_EXPLICITOS:
        codigo = "cobra_public_equivalent" if nombre in EQUIVALENCIAS_PROHIBIDAS_A_CANONICAS else "explicit_forbidden_name"
        return _rechazar(nombre, simbolo, codigo, _mensaje_nombre_prohibido(nombre), metadata)

    if not callable(simbolo) and nombre not in NOMBRES_CONSTANTES_PUBLICAS_CANONICAS:
        return _rechazar(nombre, simbolo, "non_callable_not_canonical_public_constant", "solo se permiten no-callables para constantes públicas explícitas y canónicas", metadata)

    if politica_efectiva.validar_nombre_canonico_espanol_en_cobra_facing and modulo_cobra_facing and not _parece_nombre_canonico_espanol(nombre):
        return _rechazar(
            nombre,
            simbolo,
            "non_canonical_spanish_name",
            "modo estricto Cobra-facing: nombres no canónicos no se exportan",
            metadata,
        )

    if not callable(simbolo):
        return ResultadoSaneamientoSimboloUsar(
            nombre,
            simbolo,
            False,
            "public_constant",
            "constante pública explícita permitida",
            warning=True,
            metadata=metadata,
        )

    return ResultadoSaneamientoSimboloUsar(nombre, simbolo, False, "ok", "símbolo exportable", metadata=metadata)


def sanear_exportables_para_usar(
    simbolos: list[tuple[str, object]],
    *,
    politica: PoliticaSaneamientoUsar | None = None,
    modulo_origen: str | None = None,
    modulo_cobra_facing: bool = False,
) -> tuple[list[tuple[str, object]], ClasificacionSaneamientoUsar, list[ResultadoSaneamientoSimboloUsar]]:
    """Sanea una lista de símbolos candidatos para ``usar`` de forma uniforme."""

    permitidos: list[tuple[str, object]] = []
    rechazos_duros: list[ResultadoSaneamientoSimboloUsar] = []
    warnings_transicion: list[ResultadoSaneamientoSimboloUsar] = []
    for nombre, simbolo in simbolos:
        resultado = sanear_simbolo_para_usar(
            nombre,
            simbolo,
            politica=politica,
            modulo_origen=modulo_origen,
            modulo_cobra_facing=modulo_cobra_facing,
        )
        if resultado.rechazado:
            rechazos_duros.append(resultado)
            continue
        if resultado.warning:
            warnings_transicion.append(resultado)
        permitidos.append((nombre, simbolo))

    clasificacion = ClasificacionSaneamientoUsar(rechazos_duros=rechazos_duros, warnings_transicion=warnings_transicion)
    return permitidos, clasificacion, warnings_transicion
