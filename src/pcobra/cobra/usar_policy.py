"""Políticas canónicas para la instrucción `usar`."""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path

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

REPL_COBRA_MODULE_MAP: dict[str, str] = {modulo: modulo for modulo in USAR_COBRA_PUBLIC_MODULES}
USAR_COBRA_FACING_MODULE_FLAGS: dict[str, bool] = {
    modulo: True for modulo in USAR_COBRA_PUBLIC_MODULES
}

_USAR_CANONICAL_INTERNAL_PATHS: dict[str, str] = {
    # `numero` expone el contrato runtime de `usar` desde standard_library.
    "numero": "src/pcobra/standard_library/numero.py",
    # `texto` y `datos` exponen su API pública real desde standard_library.
    "texto": "src/pcobra/standard_library/texto.py",
    "datos": "src/pcobra/standard_library/datos.py",
    "logica": "src/pcobra/corelibs/logica.py",
    "asincrono": "src/pcobra/corelibs/asincrono.py",
    "sistema": "src/pcobra/corelibs/sistema.py",
    "archivo": "src/pcobra/corelibs/archivo.py",
    "tiempo": "src/pcobra/corelibs/tiempo.py",
    "red": "src/pcobra/corelibs/red.py",
    "holobit": "src/pcobra/corelibs/holobit.py",
}


def _build_repl_cobra_module_internal_path_map() -> dict[str, str]:
    """Construye el mapeo oficial `alias usar` -> ruta interna por módulo."""

    return dict(_USAR_CANONICAL_INTERNAL_PATHS)


# Fuente única de verdad: alias canónico `usar` -> ruta interna oficial.
REPL_COBRA_MODULE_INTERNAL_PATH_MAP: dict[str, str] = _build_repl_cobra_module_internal_path_map()



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

    repo_root = Path(__file__).resolve().parents[3]
    for alias, rel_path in REPL_COBRA_MODULE_INTERNAL_PATH_MAP.items():
        if not rel_path.startswith(("src/pcobra/corelibs/", "src/pcobra/standard_library/")):
            raise RuntimeError(
                "[STARTUP CONTRACT] Las rutas internas oficiales de `usar` deben "
                f"estar en corelibs/standard_library; alias={alias} ruta={rel_path}."
            )
        path = repo_root / rel_path
        if not path.exists():
            raise RuntimeError(
                "[STARTUP CONTRACT] Falta módulo canónico obligatorio de `usar`: "
                f"alias={alias} ruta={rel_path}."
            )


validar_contrato_modulos_canonicos_usar()


@dataclass(frozen=True)
class CanonicalModuleSurfaceContract:
    required_functions: tuple[str, ...]
    allowed_aliases: dict[str, str]
    forbidden_symbols: tuple[str, ...]


CANONICAL_MODULE_SURFACE_CONTRACTS: dict[str, CanonicalModuleSurfaceContract] = {
    "numero": CanonicalModuleSurfaceContract(
        required_functions=("absoluto", "redondear", "es_par", "aleatorio", "factorial", "promedio"),
        allowed_aliases={},
        forbidden_symbols=("math", "random"),
    ),
    "texto": CanonicalModuleSurfaceContract(
        required_functions=("mayusculas", "minusculas", "dividir", "reemplazar"),
        allowed_aliases={},
        forbidden_symbols=("codecs", "re"),
    ),
    "datos": CanonicalModuleSurfaceContract(
        required_functions=("filtrar", "mapear", "agregar", "longitud"),
        allowed_aliases={},
        forbidden_symbols=("itertools",),
    ),
    "logica": CanonicalModuleSurfaceContract(
        required_functions=("conjuncion", "disyuncion", "negacion", "condicional"),
        allowed_aliases={"si_condicional": "condicional"},
        forbidden_symbols=("inspect", "product"),
    ),
    "asincrono": CanonicalModuleSurfaceContract(
        required_functions=("proteger_tarea", "limitar_tiempo", "recolectar", "grupo_tareas"),
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
        required_functions=("obtener_url", "enviar_post", "obtener_url_async", "obtener_json", "obtener_url_texto"),
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
}

# Excepciones de exportación pública por módulo para runtime `usar`.
USAR_RUNTIME_EXPORT_OVERRIDES: dict[str, tuple[str, ...]] = {
    "numero": (
        "es_finito",
        "es_infinito",
        "es_nan",
        "copiar_signo",
        "signo",
        "limitar",
        "hipotenusa",
        "distancia_euclidiana",
        "raiz_entera",
        "combinaciones",
        "permutaciones",
        "suma_precisa",
        "interpolar",
        "envolver_modular",
        "varianza",
        "varianza_muestral",
        "media_geometrica",
        "media_armonica",
        "percentil",
        "cuartiles",
        "rango_intercuartil",
        "coeficiente_variacion",
        "absoluto",
        "redondear",
        "piso",
        "techo",
        "mcd",
        "mcm",
        "es_cercano",
        "raiz",
        "potencia",
        "mediana",
        "moda",
        "es_par",
        "es_primo",
        "factorial",
        "promedio",
        "sumatoria",
        "producto",
    ),
    "texto": (
        "quitar_acentos",
        "normalizar_espacios",
        "es_palindromo",
        "es_anagrama",
        "codificar",
        "decodificar",
        "es_alfabetico",
        "es_alfa_numerico",
        "es_decimal",
        "es_numerico",
        "es_identificador",
        "es_imprimible",
        "es_ascii",
        "es_mayusculas",
        "es_minusculas",
        "es_titulo",
        "es_digito",
        "es_espacio",
        "quitar_prefijo",
        "quitar_sufijo",
        "a_snake",
        "a_camel",
        "quitar_envoltura",
        "prefijo_comun",
        "sufijo_comun",
        "dividir_lineas",
        "dividir_derecha",
        "encontrar",
        "encontrar_derecha",
        "subcadena_antes",
        "subcadena_despues",
        "subcadena_antes_ultima",
        "subcadena_despues_ultima",
        "indice",
        "indice_derecha",
        "contar_subcadena",
        "centrar_texto",
        "rellenar_ceros",
        "minusculas",
        "mayusculas",
        "minusculas_casefold",
        "intercambiar_mayusculas",
        "expandir_tabulaciones",
        "particionar",
        "particionar_derecha",
        "indentar_texto",
        "desindentar_texto",
        "envolver_texto",
        "acortar_texto",
        "formatear",
        "formatear_mapa",
        "tabla_traduccion",
        "traducir",
        "recortar",
        "repetir",
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
        "invertir_tabla",
        "tomar",
    ),
    "logica": (
        "es_verdadero",
        "es_falso",
        "conjuncion",
        "disyuncion",
        "negacion",
        "entonces",
        "si_no",
        "coalescer",
        "condicional",
        "xor",
        "nand",
        "nor",
        "implica",
        "equivale",
        "xor_multiple",
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
    ),
    "asincrono": (
        "grupo_tareas",
        "limitar_tiempo",
        "proteger_tarea",
        "ejecutar_en_hilo",
        "reintentar_async",
        "recolectar",
    ),
    "sistema": (
        "obtener_os",
        "ejecutar",
        "ejecutar_async",
        "ejecutar_stream",
        "obtener_env",
        "listar_dir",
        "directorio_actual",
    ),
    "archivo": (
        "leer",
        "escribir",
        "adjuntar",
        "existe",
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
        "obtener_json",
        "obtener_url_texto",
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



def validar_paridad_superficie_publica_modulos_canonicos() -> None:
    """Valida que corelibs y standard_library respeten el contrato central."""

    canonicos = tuple(USAR_COBRA_PUBLIC_MODULES)
    if set(CANONICAL_MODULE_SURFACE_CONTRACTS) != set(canonicos):
        raise RuntimeError("[STARTUP CONTRACT] Contratos de superficie incompletos o con módulos extra")

    for module_name in canonicos:
        contract = CANONICAL_MODULE_SURFACE_CONTRACTS[module_name]
        from pcobra.cobra.usar_loader import obtener_modulo_cobra_oficial

        module = obtener_modulo_cobra_oficial(module_name)
        exports = tuple(getattr(module, "__all__", ()))
        if not exports:
            raise RuntimeError(f"[STARTUP CONTRACT] {module_name} debe declarar __all__")

        expected_exports = USAR_RUNTIME_EXPORT_OVERRIDES.get(module_name)
        if expected_exports is not None and tuple(exports) != tuple(expected_exports):
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} debe exportar exactamente {expected_exports} y en ese orden"
            )

        missing_required = [name for name in contract.required_functions if name not in exports]
        if missing_required:
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} no exporta funciones requeridas: {missing_required}"
            )

        missing_aliases = [
            alias for alias, target in contract.allowed_aliases.items() if alias not in exports or target not in exports
        ]
        if missing_aliases:
            raise RuntimeError(f"[STARTUP CONTRACT] {module_name} aliases inválidos: {missing_aliases}")

        leaked_forbidden = [name for name in contract.forbidden_symbols if name in exports]
        if leaked_forbidden:
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} exporta símbolos prohibidos: {leaked_forbidden}"
            )

        leaked_internal = [
            name
            for name in exports
            if name.startswith("_") or "sdk" in name.lower() or "internal" in name.lower()
        ]
        if leaked_internal:
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} filtra símbolos internos en __all__: {leaked_internal}"
            )

        leaked_class_like = [name for name in exports if isinstance(name, str) and name[:1].isupper()]
        if leaked_class_like:
            raise RuntimeError(
                f"[STARTUP CONTRACT] {module_name} no debe exportar clases en __all__: {leaked_class_like}"
            )

        stdlib_path = Path(__file__).resolve().parents[1] / "standard_library" / f"{module_name}.py"
        if stdlib_path.exists():
            std_mod = importlib.import_module(f"pcobra.standard_library.{module_name}")
            std_exports = tuple(getattr(std_mod, "__all__", ()))
            if std_exports:
                combined_exports = set(exports) | set(std_exports)
                missing_required_combined = [
                    name for name in contract.required_functions if name not in combined_exports
                ]
                if missing_required_combined:
                    raise RuntimeError(
                        f"[STARTUP CONTRACT] Paridad incompleta en {module_name}: "
                        f"faltan funciones requeridas {missing_required_combined}"
                    )
