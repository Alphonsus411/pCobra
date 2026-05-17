"""Política de saneamiento de símbolos para la instrucción ``usar``."""

from dataclasses import dataclass, field
import logging
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
        "safe_wrapper",
        "public_api",
        "backend_exposed",
        "callable",
    }
)

USAR_METADATA_LEGACY_ALIASES = {
    "kind": "origin_kind",
    "introduced_by": "origin_kind",
    "introduced_by_usar": "origin_kind",
    "origen_tipo": "origin_kind",
    "is_public_export": "public_api",
    "wrapper_safe": "safe_wrapper",
}
USAR_METADATA_LEGACY_CONSISTENCY = {
    "origen_modulo": "module",
    "canonical_module": "module",
    "origin_module": "module",
    "exported_name": "symbol",
}
USAR_METADATA_LEGACY_BOOL_TRUE = {"is_sanitized_wrapper": "sanitized"}

# Claves legacy mantenidas solo por compatibilidad histórica.
USAR_SYMBOL_METADATA_LEGACY_KEYS = frozenset(
    set(USAR_METADATA_LEGACY_ALIASES)
    | set(USAR_METADATA_LEGACY_CONSISTENCY)
    | set(USAR_METADATA_LEGACY_BOOL_TRUE)
)

USAR_SYMBOL_METADATA_OPTIONAL_KEYS = frozenset(
    {
        "python_module",
        "callable_id",
        "stable_signature",
    }
)

USAR_SYMBOL_METADATA_FINAL_CONTRACT = {
    "required": USAR_SYMBOL_METADATA_REQUIRED_KEYS,
    "optional": USAR_SYMBOL_METADATA_OPTIONAL_KEYS,
    "constraints": {
        "origin_kind": "usar",
        "sanitized": True,
        "safe_wrapper": True,
        "public_api": True,
        "backend_exposed": False,
        "callable": bool,
    },
}

# Claves inesperadas consideradas críticas: no forman parte del contrato
# canónico ni de compatibilidad y deben bloquearse por fail-closed.
USAR_SYMBOL_METADATA_ALLOWED_KEYS = frozenset(
    {
        *USAR_SYMBOL_METADATA_REQUIRED_KEYS,
        *USAR_SYMBOL_METADATA_LEGACY_KEYS,
        *USAR_SYMBOL_METADATA_OPTIONAL_KEYS,
    }
)

CANONICAL_USAR_METADATA_SCHEMA = {
    "allowed_keys": USAR_SYMBOL_METADATA_ALLOWED_KEYS,
    "required_keys": USAR_SYMBOL_METADATA_FINAL_CONTRACT["required"],
    "value_constraints": USAR_SYMBOL_METADATA_FINAL_CONTRACT["constraints"],
    "legacy_aliases": USAR_METADATA_LEGACY_ALIASES,
    "legacy_consistency": USAR_METADATA_LEGACY_CONSISTENCY,
    "legacy_bool_true": USAR_METADATA_LEGACY_BOOL_TRUE,
}
USAR_SCHEMA_REQUIRED_KEYS = CANONICAL_USAR_METADATA_SCHEMA["required_keys"]
USAR_SCHEMA_ALLOWED_KEYS = CANONICAL_USAR_METADATA_SCHEMA["allowed_keys"]
USAR_SCHEMA_VALUE_CONSTRAINTS = CANONICAL_USAR_METADATA_SCHEMA["value_constraints"]
USAR_SCHEMA_LEGACY_ALIASES = CANONICAL_USAR_METADATA_SCHEMA["legacy_aliases"]
USAR_SCHEMA_LEGACY_CONSISTENCY = CANONICAL_USAR_METADATA_SCHEMA["legacy_consistency"]
USAR_SCHEMA_LEGACY_BOOL_TRUE = CANONICAL_USAR_METADATA_SCHEMA["legacy_bool_true"]


def _assert_usar_schema_allowed_keys_exact() -> None:
    esperadas = (
        USAR_SYMBOL_METADATA_REQUIRED_KEYS
        | USAR_SYMBOL_METADATA_LEGACY_KEYS
        | USAR_SYMBOL_METADATA_OPTIONAL_KEYS
    )
    if USAR_SCHEMA_ALLOWED_KEYS != esperadas:
        raise RuntimeError(
            "USAR_SCHEMA_ALLOWED_KEYS desalineado: debe contener exactamente canónicas + legacy conocidas + opcionales"
        )


_assert_usar_schema_allowed_keys_exact()

USAR_METADATA_SECURE_BOOL_DEFAULTS: dict[str, bool] = {
    "sanitized": True,
    "safe_wrapper": True,
    "public_api": True,
    "backend_exposed": False,
}
USAR_METADATA_SECURE_DEFAULTS: dict[str, object] = {
    **USAR_METADATA_SECURE_BOOL_DEFAULTS,
    "origin_kind": "usar",
}


def _resolver_valor_canonico_desde_aliases(
    *,
    metadata_dict: dict[str, object],
    canonical_key: str,
    alias_keys: list[str],
    symbol_name: str,
) -> None:
    if not alias_keys:
        return

    pares_valores: list[tuple[str, object]] = []
    if canonical_key in metadata_dict:
        pares_valores.append((canonical_key, metadata_dict[canonical_key]))
    pares_valores.extend((k, metadata_dict[k]) for k in alias_keys)

    representaciones: dict[str, list[str]] = {}
    for source_key, valor in pares_valores:
        representaciones.setdefault(repr(valor), []).append(source_key)

    if len(representaciones) > 1:
        valor_seguro = USAR_METADATA_SECURE_DEFAULTS.get(canonical_key)
        if valor_seguro is None:
            raise ValueError(
                f"Metadata inválida para símbolo usar '{symbol_name}': aliases inconsistentes para {canonical_key}"
            )
        if all(valor != valor_seguro for _, valor in pares_valores):
            raise ValueError(
                f"Metadata inválida para símbolo usar '{symbol_name}': aliases inconsistentes para {canonical_key} sin valor seguro"
            )
        metadata_dict[canonical_key] = valor_seguro
        return

    if canonical_key not in metadata_dict:
        metadata_dict[canonical_key] = pares_valores[0][1]


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
        "safe_wrapper": True,
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


def normalizar_metadata_simbolo_usar(raw_metadata: object, module_name: str, symbol_name: str) -> dict[str, object]:
    """Normaliza metadata de `usar` y aplica compatibilidad legacy segura.

    - Clona/sanitiza el input (`dict` obligatorio).
    - Convierte aliases legacy conocidos a claves canónicas cuando corresponda.
    - Completa campos derivados seguros (`module`, `symbol`, `sanitized`).
    - Elimina únicamente claves no canónicas cuando son aliases legacy mapeados.

    Orden contractual de uso: ``normalizar -> validar -> almacenar``.

    Contrato canónico obligatorio (fail-closed):
    - ``origin_kind`` (str): marcador de procedencia; debe ser ``"usar"``.
    - ``module`` (str): módulo Cobra-facing que exporta el símbolo.
    - ``symbol`` (str): nombre público exacto del símbolo (debe coincidir con ``nombre``).
    - ``sanitized`` (bool): confirma paso por saneamiento/envoltura segura.
    - ``safe_wrapper`` (bool): confirma que la API fue envuelta por wrapper seguro explícito.
      Para entradas de ``usar`` debe ser ``True``.
    - ``public_api`` (bool): confirma que el símbolo pertenece a la API pública permitida.
    - ``backend_exposed`` (bool): debe ser ``False`` para impedir exposición de backend.
    - ``callable`` (bool): indica explícitamente si el símbolo invocable es callable.

    Claves legacy se aceptan solo por compatibilidad histórica y no pueden
    reemplazar ni contradecir el contrato canónico. Tanto esas claves como las
    opcionales aceptadas forman parte de un snapshot estable e inmutable durante
    todo el ciclo (`usar` -> registro -> auditoría): el validador fail-closed
    exige igualdad estructural estricta y rechaza mutaciones inesperadas.
    """
    if not isinstance(raw_metadata, dict):
        raise ValueError(f"Metadata inválida para símbolo usar '{symbol_name}': tipo no permitido")

    metadata_dict = dict(raw_metadata)

    # 1) Resolver aliases en orden estable e invariable.
    aliases_normalizados: list[str] = []
    aliases_prioritarios_en_orden = (
        ("origin_kind", ["introduced_by", "introduced_by_usar", "origen_tipo"]),
        ("public_api", ["is_public_export"]),
        ("safe_wrapper", ["wrapper_safe"]),
    )
    for canonical_key, alias_keys_ordenados in aliases_prioritarios_en_orden:
        aliases_presentes = [k for k in alias_keys_ordenados if k in metadata_dict]
        if not aliases_presentes:
            continue
        aliases_normalizados.extend(aliases_presentes)
        _resolver_valor_canonico_desde_aliases(
            metadata_dict=metadata_dict,
            canonical_key=canonical_key,
            alias_keys=aliases_presentes,
            symbol_name=symbol_name,
        )

    # Alias legacy adicional (`kind -> origin_kind`) mantenido por compatibilidad.
    if "kind" in metadata_dict:
        aliases_normalizados.append("kind")
        _resolver_valor_canonico_desde_aliases(
            metadata_dict=metadata_dict,
            canonical_key="origin_kind",
            alias_keys=["kind"],
            symbol_name=symbol_name,
        )

    for legacy_key, canonical_key in USAR_SCHEMA_LEGACY_CONSISTENCY.items():
        if legacy_key in metadata_dict and canonical_key not in metadata_dict:
            metadata_dict[canonical_key] = metadata_dict[legacy_key]

    for legacy_key, canonical_key in USAR_SCHEMA_LEGACY_BOOL_TRUE.items():
        if legacy_key in metadata_dict and canonical_key not in metadata_dict:
            metadata_dict[canonical_key] = metadata_dict[legacy_key]

    if isinstance(module_name, str) and module_name.strip():
        if "module" in metadata_dict and metadata_dict["module"] != module_name:
            raise ValueError(
                f"Metadata inválida para símbolo usar '{symbol_name}': inconsistencia semántica: module distinto del contexto"
            )
        metadata_dict.setdefault("module", module_name)
    if isinstance(symbol_name, str) and symbol_name.strip():
        if "symbol" in metadata_dict and metadata_dict["symbol"] != symbol_name:
            raise ValueError(
                f"Metadata inválida para símbolo usar '{symbol_name}': inconsistencia semántica: symbol distinto del contexto"
            )
        metadata_dict.setdefault("symbol", symbol_name)
    # 2) Aplicar defaults seguros solo cuando faltan claves canónicas.
    metadata_dict.setdefault("origin_kind", USAR_SCHEMA_VALUE_CONSTRAINTS["origin_kind"])
    for key, default in USAR_METADATA_SECURE_BOOL_DEFAULTS.items():
        metadata_dict.setdefault(key, default)

    for legacy_key in aliases_normalizados:
        if legacy_key != USAR_SCHEMA_LEGACY_ALIASES[legacy_key]:
            metadata_dict.pop(legacy_key, None)
    for optional_legacy_key in set(USAR_METADATA_LEGACY_CONSISTENCY) | set(USAR_METADATA_LEGACY_BOOL_TRUE):
        metadata_dict.pop(optional_legacy_key, None)


    if aliases_normalizados:
        logging.info(
            "USAR metadata legacy normalizada OK module=%s symbol=%s aliases=%s",
            module_name,
            symbol_name,
            sorted(aliases_normalizados),
        )

    # 3) Evaluar claves críticas inesperadas con fail-closed, al final del
    # pipeline de normalización/control de compatibilidad.
    inesperadas_criticas = set(metadata_dict.keys()) - USAR_SCHEMA_ALLOWED_KEYS
    if inesperadas_criticas:
        raise ValueError(
            "Metadata inválida para símbolo usar "
            f"'{symbol_name}': claves desconocidas potencialmente maliciosas {sorted(inesperadas_criticas)}"
        )

    faltantes = USAR_SCHEMA_REQUIRED_KEYS - set(metadata_dict.keys())
    if faltantes:
        raise ValueError(f"Metadata inválida para símbolo usar '{symbol_name}': faltan claves {sorted(faltantes)}")

    claves_canonicas_y_opcionales = (
        USAR_SCHEMA_REQUIRED_KEYS
        | USAR_SYMBOL_METADATA_OPTIONAL_KEYS
    )
    metadata_final = {
        clave: metadata_dict[clave]
        for clave in metadata_dict
        if clave in claves_canonicas_y_opcionales
    }

    return metadata_final


def validate_usar_symbol_metadata(nombre: str, metadata: object) -> dict[str, object]:
    """Valida el contrato canónico de metadata `usar` (única puerta de validación).

    Secuencia fija exigida: ``normalizar -> validar constraints -> devolver payload canónico``.

    # SEGURIDAD
    # Este validador es fail-closed y centraliza todo control de integridad
    # antes de sincronizar metadata con intérprete/validadores semánticos.
    """
    module_name = str(metadata.get("module")) if isinstance(metadata, dict) and metadata.get("module") is not None else ""
    try:
        metadata_dict = normalizar_metadata_simbolo_usar(metadata, module_name, nombre)
    except ValueError as exc:
        mensaje = str(exc)
        detalle = "legacy normalizable" if "legacy" in mensaje else "violación de seguridad"
        logging.error(
            "USAR rechazo tras normalizar (%s) module=%s symbol=%s error=%s",
            detalle,
            module_name,
            nombre,
            mensaje,
        )
        raise ValueError(f"{mensaje} [troubleshooting: {detalle}]") from exc

    faltantes = USAR_SCHEMA_REQUIRED_KEYS - set(metadata_dict.keys())
    if faltantes:
        raise ValueError(
            f"Metadata inválida para símbolo usar '{nombre}': faltan claves {sorted(faltantes)} [troubleshooting: violación de seguridad]"
        )

    if metadata_dict.get("origin_kind") != USAR_SCHEMA_VALUE_CONSTRAINTS["origin_kind"]:
        raise ValueError(
            f"Metadata inválida para símbolo usar '{nombre}': origin_kind debe ser 'usar' [troubleshooting: violación de seguridad]"
        )

    module = metadata_dict.get("module")
    if not isinstance(module, str) or not module.strip():
        raise ValueError(
            f"Metadata inválida para símbolo usar '{nombre}': module no canónico [troubleshooting: violación de seguridad]"
        )

    symbol = metadata_dict.get("symbol")
    if not isinstance(symbol, str) or symbol != nombre:
        raise ValueError(
            f"Metadata inválida para símbolo usar '{nombre}': module/symbol no coinciden con el contexto [troubleshooting: violación de seguridad]"
        )

    if metadata_dict.get("public_api") is not USAR_SCHEMA_VALUE_CONSTRAINTS["public_api"]:
        raise ValueError(
            f"Metadata inválida para símbolo usar '{nombre}': public_api debe ser True [troubleshooting: violación de seguridad]"
        )
    if metadata_dict.get("backend_exposed") is not USAR_SCHEMA_VALUE_CONSTRAINTS["backend_exposed"]:
        raise ValueError(
            f"Metadata inválida para símbolo usar '{nombre}': backend_exposed debe ser False [troubleshooting: violación de seguridad]"
        )
    if metadata_dict.get("safe_wrapper") is not metadata_dict.get("sanitized"):
        raise ValueError(
            f"Metadata inválida para símbolo usar '{nombre}': safe_wrapper contradice sanitized [troubleshooting: violación de seguridad]"
        )
    if not isinstance(metadata_dict.get("callable"), USAR_SCHEMA_VALUE_CONSTRAINTS["callable"]):
        raise ValueError(
            f"Metadata inválida para símbolo usar '{nombre}': callable debe ser booleano [troubleshooting: violación de seguridad]"
        )

    return metadata_dict


def validate_usar_symbol_metadata_normalized(nombre: str, metadata: object) -> dict[str, object]:
    """Valida metadata `usar` exigiendo payload ya normalizado (sin claves legacy)."""
    if not isinstance(metadata, dict):
        raise ValueError(
            f"Metadata inválida para símbolo usar '{nombre}': payload no normalizado (se esperaba dict) [troubleshooting: legacy normalizable]"
        )
    legacy_presentes = set(metadata).intersection(USAR_SYMBOL_METADATA_LEGACY_KEYS)
    if legacy_presentes:
        raise ValueError(
            f"Metadata inválida para símbolo usar '{nombre}': payload no normalizado, contiene claves legacy {sorted(legacy_presentes)} [troubleshooting: legacy normalizable]"
        )
    return validate_usar_symbol_metadata(nombre, metadata)
