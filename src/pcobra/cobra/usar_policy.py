"""Políticas canónicas para la instrucción `usar`."""

from __future__ import annotations

from pathlib import Path

from pcobra.cobra.usar_loader import USAR_COBRA_PUBLIC_MODULES

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
