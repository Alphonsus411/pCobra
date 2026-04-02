#!/usr/bin/env python3
"""
Script alternativo a 'make check' para validar el proyecto Cobra
Verifica: ruff, mypy, bandit, pytest, pyright
"""

import subprocess
import sys
import shutil

TOOLS = {
    "ruff": ["ruff", "check", "src"],
    "mypy": ["mypy", "src"],
    "bandit": ["bandit", "-r", "src"],
    "pytest": ["pytest", "--cov=src", "tests", "--cov-report=term-missing"],
    "pyright": ["pyright"],
}

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
    for name, command in TOOLS.items():
        if not run_check(name, command):
            all_passed = False

    if all_passed:
        print("🎉 Todo en orden. ¡Cobra está listo para release o commit!")
        sys.exit(0)
    else:
        print("🚨 Errores detectados. Revisa los mensajes anteriores.")
        sys.exit(1)

if __name__ == "__main__":
    main()
