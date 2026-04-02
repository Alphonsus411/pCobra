#!/usr/bin/env python3
"""
Script alternativo a 'make check' para validar el proyecto Cobra.
Orden recomendado:
1) smoke de sintaxis, 2) lint/tipos, 3) pruebas completas.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from argparse import ArgumentParser

TOOLS_BY_PROFILE = {
    "solo-cobra": [
        ("smoke-syntax", [sys.executable, "scripts/smoke_syntax.py"]),
        ("ruff", ["ruff", "check", "src"]),
        ("mypy", ["mypy", "src"]),
    ],
    "transpiladores": [
        ("smoke-transpilers-syntax", [sys.executable, "scripts/smoke_transpilers_syntax.py"]),
    ],
    "completo": [
        ("smoke-syntax", [sys.executable, "scripts/smoke_syntax.py"]),
        ("smoke-transpilers-syntax", [sys.executable, "scripts/smoke_transpilers_syntax.py"]),
        ("ruff", ["ruff", "check", "src"]),
        ("mypy", ["mypy", "src"]),
        ("bandit", ["bandit", "-r", "src"]),
        ("pyright", ["pyright"]),
        ("pytest", ["pytest", "--cov=src", "tests", "--cov-report=term-missing"]),
    ],
}
PROFILE_ALIASES = {"rapido": "solo-cobra", "rápido": "solo-cobra"}


def run_check(name, command):
    if shutil.which(command[0]) is None:
        print(f"❌ {name}: no encontrado. Instálalo con pip o npm.")
        return False
    print(f"🔍 Ejecutando {name}...")
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"❌ {name} falló.\n")
        return False
    print(f"✅ {name} OK.\n")
    return True


def _parse_args() -> tuple[str, bool]:
    parser = ArgumentParser(description="Ejecuta checks por perfil para pipelines de Cobra.")
    parser.add_argument(
        "--perfil",
        default="completo",
        choices=["solo-cobra", "transpiladores", "completo", "rapido", "rápido"],
        help="Perfil: solo-cobra (rápido), transpiladores, completo.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Detiene la ejecución al primer check fallido.",
    )
    args = parser.parse_args()
    profile = PROFILE_ALIASES.get(args.perfil, args.perfil)
    return profile, bool(args.fail_fast)


def main():
    profile, fail_fast = _parse_args()
    tools = TOOLS_BY_PROFILE[profile]
    print(f"🧪 Perfil seleccionado: {profile}")

    all_passed = True
    for name, command in tools:
        if not run_check(name, command):
            all_passed = False
            if fail_fast:
                break

    if all_passed:
        print("🎉 Todo en orden. ¡Cobra está listo para release o commit!")
        sys.exit(0)

    print("🚨 Errores detectados. Revisa los mensajes anteriores.")
    sys.exit(1)


if __name__ == "__main__":
    main()
