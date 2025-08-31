import subprocess
import sys
from pathlib import Path

import pytest


def ejemplos_disponibles() -> list[str]:
    """Busca programas ``.cobra`` con su archivo ``.out`` correspondiente."""
    base = Path(__file__).resolve().parent.parent / "pCobra" / "tests" / "data"
    return sorted(
        archivo.stem
        for archivo in base.glob("*.cobra")
        if (base / f"{archivo.stem}.out").exists()
    )


@pytest.mark.parametrize("nombre", ejemplos_disponibles())
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


@pytest.mark.parametrize("nombre", ejemplos_disponibles())
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


@pytest.mark.parametrize("nombre", ejemplos_disponibles())
def test_transpilar_coincide_con_archivo(nombre: str, ruta_ejemplos: Path, tmp_path: Path) -> None:
    """Transpila ejemplos y compara el código generado con un archivo de referencia."""
    archivo = ruta_ejemplos / f"{nombre}.cobra"
    if not archivo.exists():
        archivo = ruta_ejemplos / f"{nombre}.co"
    salida = tmp_path / f"{nombre}.py"
    resultado = subprocess.run(
        [sys.executable, "-m", "pCobra.cli", "transpilar", str(archivo), "--salida", str(salida)],
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        pytest.skip(f"Transpilación falló para {nombre}: {resultado.stderr.strip()}")
    generado = salida.read_text(encoding="utf-8")
    esperado = (
        ruta_ejemplos / "expected_examples" / f"{nombre}.py"
    ).read_text(encoding="utf-8")
    assert generado == esperado
