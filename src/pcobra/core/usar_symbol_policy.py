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


USAR_SYMBOL_METADATA_REQUIRED_KEYS = frozenset(
    {
        "origin_kind",
        "module",
        "symbol",
        "sanitized",
        "public_api",
        "backend_exposed",
        "callable",
    }
)

# Claves legacy mantenidas solo por compatibilidad histórica.
USAR_SYMBOL_METADATA_LEGACY_KEYS = frozenset(
    {
        "kind",
        "origen_modulo",
        "canonical_module",
        "origin_module",
        "exported_name",
        "is_sanitized_wrapper",
    }
)

USAR_SYMBOL_METADATA_OPTIONAL_KEYS = frozenset(
    {
        "python_module",
        "callable_id",
        "stable_signature",
    }
)

# Claves inesperadas consideradas críticas: no forman parte del contrato
# canónico ni de compatibilidad y deben bloquearse por fail-closed.
USAR_SYMBOL_METADATA_ALLOWED_KEYS = (
    USAR_SYMBOL_METADATA_REQUIRED_KEYS
    | USAR_SYMBOL_METADATA_LEGACY_KEYS
    | USAR_SYMBOL_METADATA_OPTIONAL_KEYS
)

CANONICAL_USAR_METADATA_SCHEMA = {
    "allowed_keys": USAR_SYMBOL_METADATA_ALLOWED_KEYS,
    "required_keys": USAR_SYMBOL_METADATA_REQUIRED_KEYS,
    "value_constraints": {
        "origin_kind": "usar",
        "sanitized": True,
        "public_api": True,
        "backend_exposed": False,
        "callable": bool,
    },
    "legacy_aliases": {"kind": "origin_kind"},
    "legacy_consistency": {
        "origen_modulo": "module",
        "canonical_module": "module",
        "origin_module": "module",
        "exported_name": "symbol",
    },
    "legacy_bool_true": {"is_sanitized_wrapper": "sanitized"},
}


def make_usar_symbol_metadata(
    module_name: str,
    symbol_name: str,
    callable_obj: object,
) -> dict[str, object]:
    """Construye metadata canónica del contrato `usar`.

    Incluye aliases legacy estrictamente para compatibilidad.
    """
    firma_estable = None
    modulo_objeto = getattr(callable_obj, "__module__", None)
    qualname = getattr(callable_obj, "__qualname__", None)
    code = getattr(callable_obj, "__code__", None)
    if modulo_objeto and qualname:
        firma_estable = f"{modulo_objeto}:{qualname}"
        if code is not None:
            firma_estable = (
                f"{firma_estable}:"
                f"{getattr(code, 'co_argcount', 'na')}:"
                f"{getattr(code, 'co_kwonlyargcount', 'na')}"
            )
    es_callable = callable(callable_obj)
    return {
        "origin_kind": "usar",
        "module": module_name,
        "symbol": symbol_name,
        "sanitized": True,
        "public_api": True,
        "backend_exposed": False,
        "callable": es_callable,
        "python_module": modulo_objeto,
        "callable_id": id(callable_obj),
        "stable_signature": firma_estable,
        # Legacy:
        "origen_modulo": module_name,
        "canonical_module": module_name,
        "origin_module": module_name,
        "exported_name": symbol_name,
        "is_sanitized_wrapper": True,
    }


def build_and_validate_usar_symbol_metadata(
    *,
    module_name: str,
    symbol_name: str,
    callable_obj: object,
) -> dict[str, object]:
    """Fábrica canónica + validación final para metadata de ``usar``.

    Este helper es la única ruta recomendada para construir metadata desde un
    símbolo en memoria: crea la estructura con
    :func:`make_usar_symbol_metadata`, valida con
    :func:`validate_usar_symbol_metadata` y devuelve una copia normalizada para
    almacenamiento/reinyección segura.
    """
    metadata = make_usar_symbol_metadata(
        module_name=module_name,
        symbol_name=symbol_name,
        callable_obj=callable_obj,
    )
    metadata_validada = validate_usar_symbol_metadata(symbol_name, metadata)
    return dict(metadata_validada)


def _normalizar_metadata_simbolo_usar(nombre: str, metadata: object) -> dict[str, object]:
    """Normaliza e inspecciona metadata `usar` sin relajar seguridad.

    Contrato canónico obligatorio (fail-closed):
    - ``origin_kind`` (str): marcador de procedencia; debe ser ``"usar"``.
    - ``module`` (str): módulo Cobra-facing que exporta el símbolo.
    - ``symbol`` (str): nombre público exacto del símbolo (debe coincidir con ``nombre``).
    - ``sanitized`` (bool): confirma paso por saneamiento/envoltura segura.
    - ``public_api`` (bool): confirma que el símbolo pertenece a la API pública permitida.
    - ``backend_exposed`` (bool): debe ser ``False`` para impedir exposición de backend.
    - ``callable`` (bool): indica explícitamente si el símbolo invocable es callable.

    Claves legacy se aceptan solo por compatibilidad histórica y no pueden
    reemplazar ni contradecir el contrato canónico. Tanto esas claves como las
    opcionales aceptadas forman parte de un snapshot estable e inmutable durante
    todo el ciclo (`usar` -> registro -> auditoría): el validador fail-closed
    exige igualdad estructural estricta y rechaza mutaciones inesperadas.
    """
    if not isinstance(metadata, dict):
        raise ValueError(f"Metadata inválida para símbolo usar '{nombre}': tipo no permitido")

    metadata_dict = dict(metadata)
    # Compatibilidad legacy estricta: aceptar `kind="usar"` como alias de
    # `origin_kind` solo cuando el campo canónico no existe.
    for legacy_key, canonical_key in CANONICAL_USAR_METADATA_SCHEMA["legacy_aliases"].items():
        if canonical_key not in metadata_dict and legacy_key in metadata_dict:
            metadata_dict[canonical_key] = metadata_dict[legacy_key]
    faltantes = CANONICAL_USAR_METADATA_SCHEMA["required_keys"] - set(metadata_dict.keys())
    if faltantes:
        raise ValueError(f"Metadata inválida para símbolo usar '{nombre}': faltan claves {sorted(faltantes)}")

    inesperadas_criticas = set(metadata_dict.keys()) - CANONICAL_USAR_METADATA_SCHEMA["allowed_keys"]
    if inesperadas_criticas:
        raise ValueError(
            "Metadata inválida para símbolo usar "
            f"'{nombre}': claves inesperadas críticas {sorted(inesperadas_criticas)}"
        )

    return metadata_dict


def validate_usar_symbol_metadata(nombre: str, metadata: object) -> dict[str, object]:
    """Valida el contrato canónico de metadata `usar` (única puerta de validación).

    # SEGURIDAD
    # Este validador es fail-closed y centraliza todo control de integridad
    # antes de sincronizar metadata con intérprete/validadores semánticos.
    """
    metadata_dict = _normalizar_metadata_simbolo_usar(nombre, metadata)

    if metadata_dict.get("origin_kind") != CANONICAL_USAR_METADATA_SCHEMA["value_constraints"]["origin_kind"]:
        raise ValueError(f"Metadata inválida para símbolo usar '{nombre}': origin_kind inválido")

    module = metadata_dict.get("module")
    if not isinstance(module, str) or not module.strip():
        raise ValueError(f"Metadata inválida para símbolo usar '{nombre}': module no canónico")

    symbol = metadata_dict.get("symbol")
    if not isinstance(symbol, str) or symbol != nombre:
        raise ValueError(f"Metadata inválida para símbolo usar '{nombre}': symbol alterado")

    if metadata_dict.get("sanitized") is not CANONICAL_USAR_METADATA_SCHEMA["value_constraints"]["sanitized"]:
        raise ValueError(f"Metadata inválida para símbolo usar '{nombre}': wrapper no sanitizado")
    if metadata_dict.get("public_api") is not CANONICAL_USAR_METADATA_SCHEMA["value_constraints"]["public_api"]:
        raise ValueError(f"Metadata inválida para símbolo usar '{nombre}': public_api inválida")
    if metadata_dict.get("backend_exposed") is not CANONICAL_USAR_METADATA_SCHEMA["value_constraints"]["backend_exposed"]:
        raise ValueError(f"Metadata inválida para símbolo usar '{nombre}': backend_exposed inválido")
    if not isinstance(metadata_dict.get("callable"), CANONICAL_USAR_METADATA_SCHEMA["value_constraints"]["callable"]):
        raise ValueError(f"Metadata inválida para símbolo usar '{nombre}': callable debe ser booleano")

    # Compatibilidad legacy estricta: nunca reemplaza/contradice canónico.
    for legacy_key, canonical_key in CANONICAL_USAR_METADATA_SCHEMA["legacy_consistency"].items():
        if legacy_key in metadata_dict and metadata_dict[legacy_key] != metadata_dict.get(canonical_key):
            raise ValueError(
                f"Metadata inválida para símbolo usar '{nombre}': {legacy_key} contradice {canonical_key}"
            )

    for legacy_key, canonical_key in CANONICAL_USAR_METADATA_SCHEMA["legacy_bool_true"].items():
        if legacy_key in metadata_dict and metadata_dict[legacy_key] is not metadata_dict.get(canonical_key):
            raise ValueError(
                f"Metadata inválida para símbolo usar '{nombre}': {legacy_key} contradice {canonical_key}"
            )

    return metadata_dict
