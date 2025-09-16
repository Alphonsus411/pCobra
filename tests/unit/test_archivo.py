import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import standard_library.archivo as archivo


def test_archivo(tmp_path, monkeypatch):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    nombre = "f.txt"
    archivo.escribir(nombre, "hola")
    assert archivo.existe(nombre)
    archivo.adjuntar(nombre, " mundo")
    assert archivo.leer(nombre) == "hola mundo"
    os.remove(tmp_path / nombre)
    assert not archivo.existe(nombre)


@pytest.mark.parametrize(
    "func",
    [archivo.leer, lambda ruta: archivo.escribir(ruta, "dato")],
)
@pytest.mark.parametrize(
    "ruta",
    [
        lambda base: str((base / "absoluta.txt").resolve()),
        lambda _base: "../escape.txt",
    ],
)
def test_archivo_rechaza_rutas_invalidas(monkeypatch, tmp_path, func, ruta):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    with pytest.raises(ValueError):
        func(ruta(tmp_path))

