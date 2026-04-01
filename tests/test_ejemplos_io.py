import subprocess
import sys
from pathlib import Path

import pytest


def ejemplos_disponibles() -> list[str]:
    """Busca programas ``.cobra``/``.co`` con su archivo ``.out`` correspondiente."""
    base = Path(__file__).resolve().parent / "data"
    ejemplos = sorted(
        {
            archivo.stem
            for patron in ("*.cobra", "*.co")
            for archivo in base.glob(patron)
            if (base / f"{archivo.stem}.out").exists()
        }
    )
    assert ejemplos, f"No se encontraron ejemplos válidos en {base}"
    return ejemplos


@pytest.mark.parametrize("nombre", ejemplos_disponibles())
def test_ejecutar_ejemplos(nombre: str, ruta_ejemplos: Path) -> None:
    """Ejecuta programas de ejemplo y compara la salida con su archivo .out."""
    archivo = ruta_ejemplos / f"{nombre}.cobra"
    if not archivo.exists():
        archivo = ruta_ejemplos / f"{nombre}.co"
    esperado = (ruta_ejemplos / f"{nombre}.out").read_text(encoding="utf-8").strip()
    comando = [sys.executable, "-m", "pcobra.cli", "ejecutar", str(archivo)]
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        mensaje = (
            f"Ejecución falló para {nombre}\n"
            f"Comando: {' '.join(comando)}\n"
            f"stderr:\n{resultado.stderr.strip() or '<vacío>'}"
        )
        if resultado.stdout.strip():
            mensaje += f"\nstdout:\n{resultado.stdout.strip()}"
        pytest.fail(mensaje)
    salida = resultado.stdout.strip().splitlines()[-1]
    assert salida == esperado


@pytest.mark.parametrize("nombre", ejemplos_disponibles())
def test_transpilar_muestra_fragmentos(nombre: str, ruta_ejemplos: Path) -> None:
    """Transpila ejemplos y valida que el código contenga fragmentos esperados."""
    archivo = ruta_ejemplos / f"{nombre}.cobra"
    if not archivo.exists():
        archivo = ruta_ejemplos / f"{nombre}.co"
    comando = [sys.executable, "-m", "pcobra.cli", "transpilar", str(archivo)]
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        mensaje = (
            f"Transpilación falló para {nombre}\n"
            f"Comando: {' '.join(comando)}\n"
            f"stderr:\n{resultado.stderr.strip() or '<vacío>'}"
        )
        if resultado.stdout.strip():
            mensaje += f"\nstdout:\n{resultado.stdout.strip()}"
        pytest.fail(mensaje)
    assert "print(" in resultado.stdout


@pytest.mark.parametrize("nombre", ejemplos_disponibles())
def test_transpilar_coincide_con_archivo(nombre: str, ruta_ejemplos: Path, tmp_path: Path) -> None:
    """Transpila ejemplos y compara el código generado con un archivo de referencia."""
    archivo = ruta_ejemplos / f"{nombre}.cobra"
    if not archivo.exists():
        archivo = ruta_ejemplos / f"{nombre}.co"
    salida = tmp_path / f"{nombre}.py"
    comando = [sys.executable, "-m", "pcobra.cli", "transpilar", str(archivo), "--salida", str(salida)]
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        mensaje = (
            f"Transpilación falló para {nombre}\n"
            f"Comando: {' '.join(comando)}\n"
            f"stderr:\n{resultado.stderr.strip() or '<vacío>'}"
        )
        if resultado.stdout.strip():
            mensaje += f"\nstdout:\n{resultado.stdout.strip()}"
        pytest.fail(mensaje)
    generado = salida.read_text(encoding="utf-8")
    esperado = (
        ruta_ejemplos / "expected_examples" / f"{nombre}.py"
    ).read_text(encoding="utf-8")
    assert generado == esperado
