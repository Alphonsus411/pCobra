import re
import subprocess
import sys
from pathlib import Path

import pytest

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def ejemplos_disponibles() -> list[str]:
    """Busca programas ``.cobra`` con su archivo ``.out`` correspondiente."""
    base = Path(__file__).resolve().parent / "data"
    ejemplos = sorted(
        {
            archivo.stem
            for patron in ("*.cobra",)
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


def test_suma_conserva_el_contexto_local_hasta_imprimir(ruta_ejemplos: Path) -> None:
    """Una asignación local sigue disponible para el resto de la llamada."""
    archivo = ruta_ejemplos / "suma.cobra"
    resultado = subprocess.run(
        [sys.executable, "-m", "pcobra.cli", "ejecutar", str(archivo)],
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 0, resultado.stderr or resultado.stdout
    assert resultado.stdout.strip() == "5"


@pytest.mark.parametrize("nombre", ejemplos_disponibles())
def test_build_muestra_fragmentos(nombre: str, ruta_ejemplos: Path) -> None:
    """Construye ejemplos y valida que el código contenga fragmentos esperados."""
    archivo = ruta_ejemplos / f"{nombre}.cobra"
    comando = [sys.executable, "-m", "pcobra.cli", "build", str(archivo)]
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        mensaje = (
            f"Build falló para {nombre}\n"
            f"Comando: {' '.join(comando)}\n"
            f"stderr:\n{resultado.stderr.strip() or '<vacío>'}"
        )
        if resultado.stdout.strip():
            mensaje += f"\nstdout:\n{resultado.stdout.strip()}"
        pytest.fail(mensaje)
    assert "print(" in resultado.stdout


def _extraer_codigo_generado(stdout: str) -> str:
    """Obtiene el código generado después del encabezado público de ``build``."""
    salida_limpia = _ANSI_RE.sub("", stdout)
    lineas = salida_limpia.splitlines()
    for indice, linea in enumerate(lineas):
        if linea.startswith("Ruta de artefacto:"):
            return "\n".join(lineas[indice + 1 :]).strip() + "\n"
    pytest.fail(
        "No se pudo extraer el código transpilado de la salida CLI. "
        "Asegúrate de que el comando 'build' imprima el código generado."
    )


def _resolver_snapshot_esperado(ruta_ejemplos: Path, nombre: str) -> Path:
    """Resuelve el snapshot esperado usando el esquema definitivo por extensión."""
    base = ruta_ejemplos / "expected_examples"
    candidatos = (base / f"{nombre}.py", base / f"{nombre}.txt")
    for candidato in candidatos:
        if candidato.exists():
            return candidato
    pytest.fail(
        "No existe snapshot esperado para "
        f"'{nombre}'. Se buscó en: {', '.join(str(p) for p in candidatos)}. "
        "Regenera snapshots en tests/data/expected_examples/."
    )


@pytest.mark.parametrize("nombre", ejemplos_disponibles())
def test_build_coincide_con_archivo(nombre: str, ruta_ejemplos: Path) -> None:
    """Construye ejemplos y compara el código generado con el snapshot versionado."""
    archivo = ruta_ejemplos / f"{nombre}.cobra"
    comando = [sys.executable, "-m", "pcobra.cli", "build", str(archivo)]
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        mensaje = (
            f"Build falló para {nombre}\n"
            f"Comando: {' '.join(comando)}\n"
            f"stderr:\n{resultado.stderr.strip() or '<vacío>'}"
        )
        if resultado.stdout.strip():
            mensaje += f"\nstdout:\n{resultado.stdout.strip()}"
        pytest.fail(mensaje)
    generado = _extraer_codigo_generado(resultado.stdout)
    snapshot = _resolver_snapshot_esperado(ruta_ejemplos, nombre)
    esperado = snapshot.read_text(encoding="utf-8")
    assert generado == esperado
