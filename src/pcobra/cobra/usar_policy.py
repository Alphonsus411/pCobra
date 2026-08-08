"""Políticas canónicas para la instrucción `usar`."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field, replace

# Fuente única de verdad de módulos canónicos permitidos por `usar`.
USAR_COBRA_PUBLIC_MODULES: tuple[str, ...] = (
    "numero",
    "texto",
    "datos",
    "logica",
    "asincrono",
    "sistema",
    "archivo",
    "tiempo",
    "red",
    "holobit",
    "ruta",
    "serializacion",
    "proceso",
    "registro",
    "argumentos",
    "pruebas",
    "temporal",
    "cripto",
    "regex",
    "compresion",
    "configuracion",
)
USAR_COBRA_ALLOWLIST: frozenset[str] = frozenset(USAR_COBRA_PUBLIC_MODULES)
USAR_BACKEND_BLOCKLIST: frozenset[str] = frozenset(
    {
        "numpy",
        "node-fetch",
        "serde",
        "holobit_sdk",
        "pandas",
        "torch",
    }
)

REPL_COBRA_MODULE_MAP: dict[str, str] = {
    modulo: modulo for modulo in USAR_COBRA_PUBLIC_MODULES
}
USAR_COBRA_FACING_MODULE_FLAGS: dict[str, bool] = {
    modulo: True for modulo in USAR_COBRA_PUBLIC_MODULES
}

REPL_COBRA_MODULE_PACKAGE_MAP: dict[str, str] = {
    # `numero` expone el contrato runtime de `usar` desde corelibs.
    "numero": "pcobra.corelibs.numero",
    # `texto` expone su API Cobra-facing desde corelibs para evitar inicializar agregadores.
    "texto": "pcobra.standard_library.texto",
    # `datos` mantiene la misma estrategia que `numero`: el alias público se
    # resuelve por la ruta interna canónica declarada aquí.  En este caso el
    # contrato runtime apunta explícitamente a standard_library.
    "datos": "pcobra.standard_library.datos",
    **{
        alias: f"pcobra.corelibs.{alias}"
        for alias in USAR_COBRA_PUBLIC_MODULES
        if alias not in {"numero", "texto", "datos"}
    },
}


# Contrato legacy para consumidores que resuelven archivos desde la raíz del
# checkout. Es deliberadamente distinto del mapa de nombres importables.
REPL_COBRA_MODULE_INTERNAL_PATH_MAP: dict[str, str] = {
    alias: "src/" + package_name.replace(".", "/") + ".py"
    for alias, package_name in REPL_COBRA_MODULE_PACKAGE_MAP.items()
}


def validar_contrato_modulos_canonicos_usar() -> None:
    """Valida en arranque el contrato canónico de módulos para `usar` en REPL."""

    canonicos = tuple(USAR_COBRA_PUBLIC_MODULES)
    if tuple(REPL_COBRA_MODULE_MAP.keys()) != canonicos:
        raise RuntimeError(
            "[STARTUP CONTRACT] REPL_COBRA_MODULE_MAP debe incluir exactamente "
            f"los módulos canónicos soportados y en el orden oficial: {canonicos}."
        )
    if tuple(REPL_COBRA_MODULE_MAP.values()) != canonicos:
        raise RuntimeError(
            "[STARTUP CONTRACT] REPL_COBRA_MODULE_MAP debe resolver cada alias "
            "canónico a su módulo Cobra-facing oficial."
        )
    if tuple(USAR_COBRA_FACING_MODULE_FLAGS.keys()) != canonicos:
        raise RuntimeError(
            "[STARTUP CONTRACT] USAR_COBRA_FACING_MODULE_FLAGS debe declarar "
            "todos los módulos canónicos y en el orden oficial."
        )
    if not all(USAR_COBRA_FACING_MODULE_FLAGS.values()):
        raise RuntimeError(
            "[STARTUP CONTRACT] Todos los módulos canónicos de `usar` deben "
            "estar marcados como Cobra-facing."
        )

    faltantes = [m for m in canonicos if m not in REPL_COBRA_MODULE_INTERNAL_PATH_MAP]
    sobrantes = [m for m in REPL_COBRA_MODULE_INTERNAL_PATH_MAP if m not in canonicos]
    if faltantes or sobrantes:
        raise RuntimeError(
            "[STARTUP CONTRACT] REPL_COBRA_MODULE_INTERNAL_PATH_MAP fuera de contrato. "
            f"faltantes={faltantes} sobrantes={sobrantes}."
        )

    for alias, package_name in REPL_COBRA_MODULE_PACKAGE_MAP.items():
        if not package_name.startswith(
            ("pcobra.corelibs.", "pcobra.standard_library.")
        ):
            raise RuntimeError(
                "[STARTUP CONTRACT] Las rutas internas oficiales de `usar` deben "
                f"estar en corelibs/standard_library; alias={alias} paquete={package_name}."
            )
        try:
            spec = importlib.util.find_spec(package_name)
        except (ImportError, AttributeError, ValueError):
            spec = None
        if spec is None:
            raise RuntimeError(
                "[STARTUP CONTRACT] Falta módulo canónico obligatorio de `usar`: "
                f"alias={alias} paquete={package_name}."
            )


validar_contrato_modulos_canonicos_usar()


@dataclass(frozen=True)
class CanonicalModuleSurfaceContract:
    required_functions: tuple[str, ...]
    allowed_aliases: dict[str, str]
    forbidden_symbols: tuple[str, ...]
    symbol_capabilities: dict[str, frozenset[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class FilesystemSymbolPolicy:
    """Decisión auditable para un símbolo que accede al filesystem."""

    capabilities: frozenset[str]
    sandbox_confined: bool
    safe_mode_decision: str


CANONICAL_MODULE_SURFACE_CONTRACTS: dict[str, CanonicalModuleSurfaceContract] = {
    "numero": CanonicalModuleSurfaceContract(
        required_functions=(
            "absoluto",
            "redondear",
            "es_par",
            "aleatorio",
            "factorial",
            "promedio",
        ),
        allowed_aliases={},
        forbidden_symbols=("math", "random"),
    ),
    "texto": CanonicalModuleSurfaceContract(
        required_functions=("mayusculas", "minusculas", "dividir", "reemplazar"),
        allowed_aliases={},
        forbidden_symbols=("codecs", "re"),
    ),
    "datos": CanonicalModuleSurfaceContract(
        required_functions=("filtrar", "mapear", "reducir", "longitud"),
        allowed_aliases={},
        forbidden_symbols=("itertools",),
    ),
    "logica": CanonicalModuleSurfaceContract(
        required_functions=("conjuncion", "disyuncion", "negacion", "condicional"),
        allowed_aliases={"si_condicional": "condicional"},
        forbidden_symbols=("inspect", "product"),
    ),
    "asincrono": CanonicalModuleSurfaceContract(
        required_functions=(
            "proteger_tarea",
            "limitar_tiempo",
            "recolectar",
            "grupo_tareas",
        ),
        allowed_aliases={},
        forbidden_symbols=("asyncio",),
    ),
    "sistema": CanonicalModuleSurfaceContract(
        required_functions=("obtener_os", "ejecutar", "obtener_env", "listar_dir"),
        allowed_aliases={"ejecutar_comando_async": "ejecutar_async"},
        forbidden_symbols=("subprocess", "os"),
    ),
    "archivo": CanonicalModuleSurfaceContract(
        required_functions=("leer", "escribir", "existe", "eliminar"),
        allowed_aliases={},
        forbidden_symbols=("Path",),
    ),
    "tiempo": CanonicalModuleSurfaceContract(
        required_functions=("ahora", "formatear", "dormir", "epoch"),
        allowed_aliases={},
        forbidden_symbols=("time", "datetime"),
    ),
    "red": CanonicalModuleSurfaceContract(
        required_functions=(
            "obtener_url",
            "enviar_post",
            "obtener_url_async",
            "obtener_json",
            "obtener_url_texto",
        ),
        allowed_aliases={"obtener_url_texto": "obtener_url"},
        forbidden_symbols=("requests", "httpx"),
    ),
    "holobit": CanonicalModuleSurfaceContract(
        required_functions=(
            "crear_holobit",
            "validar_holobit",
            "serializar_holobit",
            "deserializar_holobit",
            "proyectar",
            "transformar",
            "graficar",
            "combinar",
            "medir",
        ),
        allowed_aliases={},
        forbidden_symbols=("_SDKHolobit", "Holobit", "holobit_sdk"),
    ),
    "ruta": CanonicalModuleSurfaceContract(
        required_functions=(
            "unir",
            "normalizar",
            "nombre",
            "extension",
            "padre",
            "existe",
            "es_absoluta",
            "absoluta",
            "relativa",
        ),
        allowed_aliases={},
        forbidden_symbols=("Path",),
    ),
    "serializacion": CanonicalModuleSurfaceContract(
        required_functions=(
            "codificar_json",
            "decodificar_json",
            "leer_json",
            "escribir_json",
            "leer_csv",
            "escribir_csv",
        ),
        allowed_aliases={},
        forbidden_symbols=("json", "csv"),
    ),
    "proceso": CanonicalModuleSurfaceContract(
        required_functions=(
            "ejecutar",
            "capturar",
            "ejecutar_async",
            "ejecutar_stream",
            "codigo_salida",
            "salida",
            "errores",
        ),
        allowed_aliases={"capturar": "ejecutar"},
        forbidden_symbols=("subprocess",),
    ),
    "registro": CanonicalModuleSurfaceContract(
        required_functions=(
            "configurar",
            "debug",
            "info",
            "aviso",
            "error",
            "obtener_registrador",
        ),
        allowed_aliases={},
        forbidden_symbols=("logging",),
    ),
    "argumentos": CanonicalModuleSurfaceContract(
        required_functions=(
            "obtener_argumentos",
            "contiene_flag",
            "obtener_opcion",
            "parsear_pares",
        ),
        allowed_aliases={},
        forbidden_symbols=("sys",),
    ),
    "pruebas": CanonicalModuleSurfaceContract(
        required_functions=("igual", "verdadero", "falso", "contiene", "lanza_error"),
        allowed_aliases={},
        forbidden_symbols=("pytest", "unittest"),
    ),
    "temporal": CanonicalModuleSurfaceContract(
        required_functions=("archivo_temporal", "directorio_temporal", "limpiar"),
        allowed_aliases={},
        forbidden_symbols=("tempfile",),
    ),
    "cripto": CanonicalModuleSurfaceContract(
        required_functions=(
            "sha256",
            "sha512",
            "comparar_seguro",
            "token_seguro",
            "token_hexadecimal",
        ),
        allowed_aliases={},
        forbidden_symbols=("hashlib", "secrets", "hmac"),
    ),
    "regex": CanonicalModuleSurfaceContract(
        required_functions=(
            "buscar",
            "coincidir",
            "reemplazar",
            "dividir",
            "encontrar_todos",
        ),
        allowed_aliases={},
        forbidden_symbols=("re",),
    ),
    "compresion": CanonicalModuleSurfaceContract(
        required_functions=("crear_zip", "extraer_zip", "listar_zip"),
        allowed_aliases={},
        forbidden_symbols=("zipfile",),
    ),
    "configuracion": CanonicalModuleSurfaceContract(
        required_functions=(
            "leer_toml",
            "leer_ini",
            "toml_disponible",
            "leer_configuracion",
        ),
        allowed_aliases={},
        forbidden_symbols=("configparser", "tomllib"),
    ),
}

# Excepciones de exportación pública por módulo para runtime `usar`.
USAR_RUNTIME_EXPORT_OVERRIDES: dict[str, tuple[str, ...]] = {
    "numero": (
        "absoluto",
        "redondear",
        "piso",
        "techo",
        "mcd",
        "mcm",
        "es_cercano",
        "hipotenusa",
        "distancia_euclidiana",
        "es_finito",
        "es_infinito",
        "es_nan",
        "copiar_signo",
        "signo",
        "producto",
        "entero_a_base",
        "entero_desde_base",
        "longitud_bits",
        "contar_bits",
        "rotar_bits_izquierda",
        "rotar_bits_derecha",
        "entero_a_bytes",
        "entero_desde_bytes",
        "raiz",
        "raiz_entera",
        "potencia",
        "limitar",
        "interpolar",
        "envolver_modular",
        "aleatorio",
        "aleatorio_entero",
        "mediana",
        "moda",
        "desviacion_estandar",
        "es_par",
        "es_primo",
        "factorial",
        "promedio",
        "combinaciones",
        "permutaciones",
        "suma_precisa",
        "varianza",
        "varianza_muestral",
        "media_geometrica",
        "media_armonica",
        "percentil",
        "cuartiles",
        "rango_intercuartil",
        "coeficiente_variacion",
    ),
    "texto": (
        "a_snake",
        "mayusculas",
        "minusculas",
        "prefijo_comun",
        "sufijo_comun",
        "recortar",
        "repetir",
        "quitar_acentos",
        "dividir",
        "reemplazar",
    ),
    "datos": (
        "leer_csv",
        "leer_json",
        "escribir_csv",
        "escribir_json",
        "leer_excel",
        "escribir_excel",
        "leer_parquet",
        "escribir_parquet",
        "leer_feather",
        "escribir_feather",
        "describir",
        "correlacion_pearson",
        "correlacion_spearman",
        "matriz_covarianza",
        "calcular_percentiles",
        "resumen_rapido",
        "seleccionar_columnas",
        "filtrar",
        "mutar_columna",
        "separar_columna",
        "unir_columnas",
        "agrupar_y_resumir",
        "tabla_cruzada",
        "pivotar_ancho",
        "pivotar_largo",
        "ordenar_tabla",
        "combinar_tablas",
        "rellenar_nulos",
        "desplegar_tabla",
        "pivotar_tabla",
        "agregar",
        "mapear",
        "reducir",
        "claves",
        "valores",
        "longitud",
        "elemento",
        "invertir_tabla",
        "tomar",
    ),
    "logica": (
        "es_verdadero",
        "es_falso",
        "conjuncion",
        "disyuncion",
        "negacion",
        "xor",
        "nand",
        "nor",
        "implica",
        "equivale",
        "xor_multiple",
        "entonces",
        "si_no",
        "condicional",
        "coalescer",
        "todas",
        "alguna",
        "ninguna",
        "solo_uno",
        "conteo_verdaderos",
        "paridad",
        "mayoria",
        "exactamente_n",
        "tabla_verdad",
        "diferencia_simetrica",
        "si_condicional",
    ),
    "asincrono": (
        "proteger_tarea",
        "limitar_tiempo",
        "ejecutar_en_hilo",
        "recolectar",
        "carrera",
        "primero_exitoso",
        "esperar_timeout",
        "reintentar_async",
        "grupo_tareas",
        "crear_tarea",
        "iterar_completadas",
        "mapear_concurrencia",
        "recolectar_resultados",
        "dormir_async",
    ),
    "sistema": (
        "obtener_os",
        "ejecutar",
        "ejecutar_async",
        "ejecutar_stream",
        "obtener_env",
        "listar_dir",
        "ejecutar_comando_async",
        "directorio_actual",
    ),
    "archivo": (
        "leer",
        "escribir",
        "existe",
        "eliminar",
        "anexar",
        "leer_lineas",
    ),
    "tiempo": (
        "ahora",
        "formatear",
        "dormir",
        "epoch",
        "desde_epoch",
    ),
    "red": (
        "obtener_url",
        "enviar_post",
        "obtener_url_async",
        "enviar_post_async",
        "descargar_archivo",
        "obtener_url_texto",
        "obtener_json",
    ),
    "holobit": (
        "crear_holobit",
        "validar_holobit",
        "serializar_holobit",
        "deserializar_holobit",
        "proyectar",
        "transformar",
        "graficar",
        "combinar",
        "medir",
    ),
}

# Clasificación deliberadamente explícita. Un conjunto vacío significa que el
# símbolo es puro; los demás conjuntos enumeran sus efectos observables. No se
# infiere ninguna capacidad a partir del nombre del símbolo.
_EFFECTFUL_PUBLIC_SYMBOLS: dict[str, dict[str, frozenset[str]]] = {
    "numero": {
        "aleatorio": frozenset({"random.read"}),
        "aleatorio_entero": frozenset({"random.read"}),
    },
    "datos": {
        **{
            name: frozenset({"filesystem.read"})
            for name in (
                "leer_csv",
                "leer_json",
                "leer_excel",
                "leer_parquet",
                "leer_feather",
            )
        },
        **{
            name: frozenset({"filesystem.write"})
            for name in (
                "escribir_csv",
                "escribir_json",
                "escribir_excel",
                "escribir_parquet",
                "escribir_feather",
            )
        },
    },
    "asincrono": {
        **{
            name: frozenset({"async.schedule"})
            for name in (
                "proteger_tarea",
                "limitar_tiempo",
                "ejecutar_en_hilo",
                "recolectar",
                "carrera",
                "primero_exitoso",
                "esperar_timeout",
                "reintentar_async",
                "grupo_tareas",
                "crear_tarea",
                "iterar_completadas",
                "mapear_concurrencia",
                "recolectar_resultados",
                "dormir_async",
            )
        },
    },
    "sistema": {
        **{
            name: frozenset({"process.spawn"})
            for name in (
                "ejecutar",
                "ejecutar_async",
                "ejecutar_stream",
                "ejecutar_comando_async",
            )
        },
        "obtener_env": frozenset({"environment.read"}),
        "listar_dir": frozenset({"filesystem.read"}),
        "directorio_actual": frozenset({"environment.read"}),
    },
    "archivo": {
        **{
            name: frozenset({"filesystem.read"})
            for name in ("leer", "existe", "leer_lineas")
        },
        **{
            name: frozenset({"filesystem.write"})
            for name in ("escribir", "eliminar", "anexar")
        },
    },
    "tiempo": {
        "ahora": frozenset({"clock.read"}),
        "dormir": frozenset({"clock.sleep"}),
        "epoch": frozenset({"clock.read"}),
    },
    "red": {
        **{
            name: frozenset({"network.get"})
            for name in (
                "obtener_url",
                "obtener_url_async",
                "obtener_url_texto",
                "obtener_json",
            )
        },
        **{
            name: frozenset({"network.post"})
            for name in ("enviar_post", "enviar_post_async")
        },
        "descargar_archivo": frozenset({"network.download", "filesystem.write"}),
    },
    "ruta": {
        "existe": frozenset({"filesystem.read"}),
        "absoluta": frozenset({"environment.read"}),
        "relativa": frozenset({"environment.read"}),
    },
    "serializacion": {
        **{name: frozenset({"filesystem.read"}) for name in ("leer_json", "leer_csv")},
        **{
            name: frozenset({"filesystem.write"})
            for name in ("escribir_json", "escribir_csv")
        },
    },
    "proceso": {
        **{
            name: frozenset({"process.spawn"})
            for name in ("ejecutar", "capturar", "ejecutar_async", "ejecutar_stream")
        },
    },
    "registro": {
        **{
            name: frozenset({"logging.write"})
            for name in (
                "configurar",
                "debug",
                "info",
                "aviso",
                "error",
                "obtener_registrador",
            )
        },
    },
    "argumentos": {"obtener_argumentos": frozenset({"environment.read"})},
    "temporal": {
        **{
            name: frozenset({"filesystem.write"})
            for name in ("archivo_temporal", "directorio_temporal", "limpiar")
        },
    },
    "cripto": {
        "token_seguro": frozenset({"random.read"}),
        "token_hexadecimal": frozenset({"random.read"}),
    },
    "compresion": {
        "crear_zip": frozenset({"filesystem.read", "filesystem.write"}),
        "extraer_zip": frozenset({"filesystem.read", "filesystem.write"}),
        "listar_zip": frozenset({"filesystem.read"}),
    },
    "configuracion": {
        **{
            name: frozenset({"filesystem.read"})
            for name in ("leer_toml", "leer_ini", "leer_configuracion")
        },
    },
}

# Matriz canónica de confinamiento. Cada entrada corresponde a un símbolo de
# ``_EFFECTFUL_PUBLIC_SYMBOLS`` con filesystem.read/filesystem.write. Los grupos
# son enumeraciones declarativas de implementaciones auditadas, no heurísticas
# basadas en el nombre. ``allow`` sólo significa que el efecto filesystem puede
# alcanzar el runtime seguro; otras capacidades del símbolo (por ejemplo red)
# se siguen aplicando independientemente.
_FILESYSTEM_SANDBOX_CONFINEMENT: dict[str, dict[str, bool]] = {
    "datos": {
        "leer_csv": False,
        "leer_json": False,
        "leer_excel": False,
        "leer_parquet": False,
        "leer_feather": False,
        "escribir_csv": False,
        "escribir_json": False,
        "escribir_excel": False,
        "escribir_parquet": False,
        "escribir_feather": False,
    },
    "sistema": {"listar_dir": False},
    "archivo": {
        "leer": True,
        "existe": True,
        "leer_lineas": True,
        "escribir": True,
        "eliminar": True,
        "anexar": True,
    },
    "red": {"descargar_archivo": True},
    "ruta": {"existe": False},
    "serializacion": {
        "leer_json": False,
        "leer_csv": False,
        "escribir_json": False,
        "escribir_csv": False,
    },
    "temporal": {
        "archivo_temporal": False,
        "directorio_temporal": False,
        "limpiar": False,
    },
    "compresion": {
        "crear_zip": True,
        "extraer_zip": True,
        "listar_zip": True,
    },
    "configuracion": {
        "leer_toml": False,
        "leer_ini": False,
        "leer_configuracion": False,
    },
}

FILESYSTEM_SYMBOL_POLICIES: dict[tuple[str, str], FilesystemSymbolPolicy] = {
    (module_name, symbol_name): FilesystemSymbolPolicy(
        capabilities=capabilities,
        sandbox_confined=confined,
        safe_mode_decision="allow" if confined else "deny",
    )
    for module_name, symbols in _FILESYSTEM_SANDBOX_CONFINEMENT.items()
    for symbol_name, confined in symbols.items()
    for capabilities in (_EFFECTFUL_PUBLIC_SYMBOLS[module_name][symbol_name],)
}


def filesystem_policy_for(
    module_name: str, symbol_name: str
) -> FilesystemSymbolPolicy | None:
    """Consulta la matriz explícita sin deducir decisiones del identificador."""

    return FILESYSTEM_SYMBOL_POLICIES.get((module_name, symbol_name))


def _validar_matriz_filesystem() -> None:
    esperados = {
        (module_name, symbol_name)
        for module_name, symbols in _EFFECTFUL_PUBLIC_SYMBOLS.items()
        for symbol_name, capabilities in symbols.items()
        if capabilities & {"filesystem.read", "filesystem.write"}
    }
    declarados = set(FILESYSTEM_SYMBOL_POLICIES)
    if esperados != declarados:
        raise RuntimeError(
            "[STARTUP CONTRACT] Matriz filesystem incompleta: "
            f"faltantes={sorted(esperados - declarados)} "
            f"sobrantes={sorted(declarados - esperados)}"
        )


_validar_matriz_filesystem()

_PURE_PUBLIC_SYMBOLS: dict[str, tuple[str, ...]] = {
    "numero": (
        "absoluto",
        "redondear",
        "piso",
        "techo",
        "mcd",
        "mcm",
        "es_cercano",
        "hipotenusa",
        "distancia_euclidiana",
        "es_finito",
        "es_infinito",
        "es_nan",
        "copiar_signo",
        "signo",
        "producto",
        "entero_a_base",
        "entero_desde_base",
        "longitud_bits",
        "contar_bits",
        "rotar_bits_izquierda",
        "rotar_bits_derecha",
        "entero_a_bytes",
        "entero_desde_bytes",
        "raiz",
        "raiz_entera",
        "potencia",
        "limitar",
        "interpolar",
        "envolver_modular",
        "mediana",
        "moda",
        "desviacion_estandar",
        "es_par",
        "es_primo",
        "factorial",
        "promedio",
        "combinaciones",
        "permutaciones",
        "suma_precisa",
        "varianza",
        "varianza_muestral",
        "media_geometrica",
        "media_armonica",
        "percentil",
        "cuartiles",
        "rango_intercuartil",
        "coeficiente_variacion",
    ),
    "texto": (
        "a_snake",
        "mayusculas",
        "minusculas",
        "prefijo_comun",
        "sufijo_comun",
        "recortar",
        "repetir",
        "quitar_acentos",
        "dividir",
        "reemplazar",
    ),
    "datos": (
        "describir",
        "correlacion_pearson",
        "correlacion_spearman",
        "matriz_covarianza",
        "calcular_percentiles",
        "resumen_rapido",
        "seleccionar_columnas",
        "filtrar",
        "mutar_columna",
        "separar_columna",
        "unir_columnas",
        "agrupar_y_resumir",
        "tabla_cruzada",
        "pivotar_ancho",
        "pivotar_largo",
        "ordenar_tabla",
        "combinar_tablas",
        "rellenar_nulos",
        "desplegar_tabla",
        "pivotar_tabla",
        "agregar",
        "mapear",
        "reducir",
        "claves",
        "valores",
        "longitud",
        "elemento",
        "invertir_tabla",
        "tomar",
    ),
    "logica": (
        "es_verdadero",
        "es_falso",
        "conjuncion",
        "disyuncion",
        "negacion",
        "xor",
        "nand",
        "nor",
        "implica",
        "equivale",
        "xor_multiple",
        "entonces",
        "si_no",
        "condicional",
        "coalescer",
        "todas",
        "alguna",
        "ninguna",
        "solo_uno",
        "conteo_verdaderos",
        "paridad",
        "mayoria",
        "exactamente_n",
        "tabla_verdad",
        "diferencia_simetrica",
        "si_condicional",
    ),
    "asincrono": (),
    "sistema": ("obtener_os",),
    "archivo": (),
    "tiempo": ("formatear", "desde_epoch"),
    "red": (),
    "holobit": (
        "crear_holobit",
        "validar_holobit",
        "serializar_holobit",
        "deserializar_holobit",
        "proyectar",
        "transformar",
        "graficar",
        "combinar",
        "medir",
    ),
    "ruta": ("unir", "normalizar", "nombre", "extension", "padre", "es_absoluta"),
    "serializacion": ("codificar_json", "decodificar_json"),
    "proceso": ("codigo_salida", "salida", "errores"),
    "registro": (),
    "argumentos": ("contiene_flag", "obtener_opcion", "parsear_pares"),
    "pruebas": ("igual", "verdadero", "falso", "contiene", "lanza_error"),
    "temporal": (),
    "cripto": ("sha256", "sha512", "comparar_seguro"),
    "regex": ("buscar", "coincidir", "reemplazar", "dividir", "encontrar_todos"),
    "compresion": (),
    "configuracion": ("toml_disponible",),
}

for _module_name, _contract in tuple(CANONICAL_MODULE_SURFACE_CONTRACTS.items()):
    _capabilities = {name: frozenset() for name in _PURE_PUBLIC_SYMBOLS[_module_name]}
    _capabilities.update(_EFFECTFUL_PUBLIC_SYMBOLS.get(_module_name, {}))
    CANONICAL_MODULE_SURFACE_CONTRACTS[_module_name] = replace(
        _contract, symbol_capabilities=_capabilities
    )


def validar_paridad_superficie_publica_modulos_canonicos() -> None:
    """Valida que corelibs y standard_library respeten el contrato central."""

    canonicos = tuple(USAR_COBRA_PUBLIC_MODULES)
    if set(CANONICAL_MODULE_SURFACE_CONTRACTS) != set(canonicos):
        raise RuntimeError(
            "[STARTUP CONTRACT] Contratos de superficie incompletos o con módulos extra"
        )

    for module_name in canonicos:
        contract = CANONICAL_MODULE_SURFACE_CONTRACTS[module_name]
        from pcobra.cobra.usar_loader import obtener_modulo_cobra_oficial

        module = obtener_modulo_cobra_oficial(module_name)
        exports = tuple(getattr(module, "__all__", ()))
        if not exports:
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} debe declarar __all__"
            )

        classified_exports = tuple(contract.symbol_capabilities)
        missing_classification = sorted(set(exports) - set(classified_exports))
        stale_classification = sorted(set(classified_exports) - set(exports))
        if missing_classification or stale_classification:
            raise RuntimeError(
                f"[STARTUP CONTRACT] Clasificación de capacidades incompleta en "
                f"{module_name}: sin_clasificar={missing_classification} "
                f"sin_exportar={stale_classification}"
            )

        expected_exports = USAR_RUNTIME_EXPORT_OVERRIDES.get(module_name)
        if expected_exports is not None and tuple(exports) != tuple(expected_exports):
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} debe exportar exactamente {expected_exports} y en ese orden"
            )

        missing_required = [
            name for name in contract.required_functions if name not in exports
        ]
        if missing_required:
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} no exporta funciones requeridas: {missing_required}"
            )

        missing_aliases = [
            alias
            for alias, target in contract.allowed_aliases.items()
            if alias not in exports or target not in exports
        ]
        if missing_aliases:
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} aliases inválidos: {missing_aliases}"
            )
        aliases_with_different_capabilities = [
            alias
            for alias, target in contract.allowed_aliases.items()
            if contract.symbol_capabilities[alias]
            != contract.symbol_capabilities[target]
        ]
        if aliases_with_different_capabilities:
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} aliases con capacidades "
                f"distintas del destino: {aliases_with_different_capabilities}"
            )

        leaked_forbidden = [
            name for name in contract.forbidden_symbols if name in exports
        ]
        if leaked_forbidden:
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} exporta símbolos prohibidos: {leaked_forbidden}"
            )

        leaked_internal = [
            name
            for name in exports
            if name.startswith("_")
            or "sdk" in name.lower()
            or "internal" in name.lower()
        ]
        if leaked_internal:
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} filtra símbolos internos en __all__: {leaked_internal}"
            )

        leaked_class_like = [
            name for name in exports if isinstance(name, str) and name[:1].isupper()
        ]
        if leaked_class_like:
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} no debe exportar clases en __all__: {leaked_class_like}"
            )

        stdlib_name = f"pcobra.standard_library.{module_name}"
        if importlib.util.find_spec(stdlib_name) is not None:
            std_mod = importlib.import_module(stdlib_name)
            std_exports = tuple(getattr(std_mod, "__all__", ()))
            if std_exports:
                combined_exports = set(exports) | set(std_exports)
                missing_required_combined = [
                    name
                    for name in contract.required_functions
                    if name not in combined_exports
                ]
                if missing_required_combined:
                    raise RuntimeError(
                        f"[STARTUP CONTRACT] Paridad incompleta en {module_name}: "
                        f"faltan funciones requeridas {missing_required_combined}"
                    )
