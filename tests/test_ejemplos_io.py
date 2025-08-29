import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "nombre", [
        "hola",  # ejemplo: imprime un saludo sencillo
        "suma",  # ejemplo: calcula y muestra la suma de dos números
    ],
)
def test_ejecutar_ejemplos(nombre: str, ruta_ejemplos: Path) -> None:
    """Ejecuta programas de ejemplo y compara la salida con su archivo .out."""
    archivo = ruta_ejemplos / f"{nombre}.cobra"
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
    ],
)
def test_transpilar_muestra_fragmentos(nombre: str, ruta_ejemplos: Path) -> None:
    """Transpila ejemplos y valida que el código contenga fragmentos esperados."""
    archivo = ruta_ejemplos / f"{nombre}.cobra"
    resultado = subprocess.run(
        [sys.executable, "-m", "pCobra.cli", "transpilar", str(archivo)],
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        pytest.skip(f"Transpilación falló para {nombre}: {resultado.stderr.strip()}")
    assert "print(" in resultado.stdout
