#!/usr/bin/env python3
"""Compila y ejecuta el ejemplo 'Hello World' usando clang."""
from __future__ import annotations
import subprocess
import time
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "examples" / "hello_world" / "c.c"
BINARY = HERE / "hello_clang.bin"


def compile_with_clang() -> float:
    """Compila el archivo de ejemplo y devuelve el tiempo empleado."""
    start = time.perf_counter()
    subprocess.run(["clang", str(SOURCE), "-o", str(BINARY)], check=True)
    return time.perf_counter() - start


def run_binary() -> tuple[str, float]:
    """Ejecuta el binario generado y devuelve su salida y el tiempo."""
    start = time.perf_counter()
    completed = subprocess.run([str(BINARY)], capture_output=True, text=True, check=True)
    elapsed = time.perf_counter() - start
    return completed.stdout.strip(), elapsed


def main() -> None:
    compile_time = compile_with_clang()
    output, run_time = run_binary()
    size = os.path.getsize(BINARY)
    print(f"Salida del programa: {output}")
    print(f"Tiempo de compilación: {compile_time:.4f} s")
    print(f"Tiempo de ejecución: {run_time:.4f} s")
    print(f"Tamaño del binario: {size} bytes")


if __name__ == "__main__":
    main()
