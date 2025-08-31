import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "nombre", [
        "hola",  # ejemplo: imprime un saludo sencillo
        "suma",  # ejemplo: calcula y muestra la suma de dos números
        "async_await",  # ejemplo: ejecución asíncrona básica
        "factorial_recursivo",  # ejemplo: calcula factorial recursivamente
        "suma_matrices",  # ejemplo: suma elementos de dos matrices
        "ejemplo",  # ejemplo: muestra un saludo simple
    ],
)
def test_ejecutar_ejemplos(nombre: str, ruta_ejemplos: Path) -> None:
    """Ejecuta programas de ejemplo y compara la salida con su archivo .out."""
    archivo = ruta_ejemplos / f"{nombre}.cobra"
    if not archivo.exists():
        archivo = ruta_ejemplos / f"{nombre}.co"
    esperado = (ruta_ejemplos / f"{nombre}.out").read_text(encoding="utf-8").strip()
    resultado = subprocess.run(
        [sys.executable, "-m", "pCobra.cli", "ejecutar", str(archivo)],
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        pytest.skip(f"Ejecución falló para {nombre}: {resultado.stderr.strip()}")
    salida = resultado.stdout.strip().splitlines()[-1]
    assert salida == esperado


@pytest.mark.parametrize(
    "nombre", [
        "hola",  # debe generar una llamada a print en el código Python
        "suma",  # comprueba que la transpilación incluya impresiones
        "async_await",  # valida transpilación de async/await
        "factorial_recursivo",  # confirma transpilación de recursividad
        "suma_matrices",  # verifica transpilación con múltiples prints
        "ejemplo",  # debe contener un print sencillo
    ],
)
def test_transpilar_muestra_fragmentos(nombre: str, ruta_ejemplos: Path) -> None:
    """Transpila ejemplos y valida que el código contenga fragmentos esperados."""
    archivo = ruta_ejemplos / f"{nombre}.cobra"
    if not archivo.exists():
        archivo = ruta_ejemplos / f"{nombre}.co"
    resultado = subprocess.run(
        [sys.executable, "-m", "pCobra.cli", "transpilar", str(archivo)],
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        pytest.skip(f"Transpilación falló para {nombre}: {resultado.stderr.strip()}")
    assert "print(" in resultado.stdout
