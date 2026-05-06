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

REPL_COBRA_MODULE_MAP: dict[str, str] = {modulo: modulo for modulo in USAR_COBRA_PUBLIC_MODULES}

# Fuente única de verdad: alias canónico `usar` -> ruta interna oficial.
REPL_COBRA_MODULE_INTERNAL_PATH_MAP: dict[str, str] = {
    "numero": "src/pcobra/corelibs/numero.py",
    "texto": "src/pcobra/corelibs/texto.py",
    "datos": "src/pcobra/corelibs/datos.py",
    "logica": "src/pcobra/corelibs/logica.py",
    "asincrono": "src/pcobra/corelibs/asincrono.py",
    "sistema": "src/pcobra/corelibs/sistema.py",
    "archivo": "src/pcobra/corelibs/archivo.py",
    "tiempo": "src/pcobra/corelibs/tiempo.py",
    "red": "src/pcobra/corelibs/red.py",
    "holobit": "src/pcobra/corelibs/holobit.py",
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
        required_functions=("absoluto", "redondear", "es_par", "aleatorio"),
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
        required_functions=("obtener_url", "enviar_post", "obtener_url_async", "obtener_json"),
        allowed_aliases={"obtener_url_texto": "obtener_url"},
        forbidden_symbols=("requests", "httpx"),
    ),
    "holobit": CanonicalModuleSurfaceContract(
        required_functions=("crear_holobit", "validar_holobit", "transformar", "graficar"),
        allowed_aliases={},
        forbidden_symbols=("_SDKHolobit",),
    ),
}

# Excepciones de exportación pública por módulo para runtime `usar`.
USAR_RUNTIME_EXPORT_OVERRIDES: dict[str, tuple[str, ...]] = {
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
    )
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
