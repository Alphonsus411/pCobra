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

TOOLS = [
    ("smoke-syntax", [sys.executable, "scripts/smoke_syntax.py"]),
    ("ruff", ["ruff", "check", "src"]),
    ("mypy", ["mypy", "src"]),
    ("bandit", ["bandit", "-r", "src"]),
    ("pyright", ["pyright"]),
    ("pytest", ["pytest", "--cov=src", "tests", "--cov-report=term-missing"]),
]


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


def main():
    all_passed = True
    for name, command in TOOLS:
        if not run_check(name, command):
            all_passed = False

    if all_passed:
        print("🎉 Todo en orden. ¡Cobra está listo para release o commit!")
        sys.exit(0)

    print("🚨 Errores detectados. Revisa los mensajes anteriores.")
    sys.exit(1)


if __name__ == "__main__":
    main()
