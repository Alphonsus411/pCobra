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


@pytest.mark.parametrize("ruta", ["README.md", "./README.md"])
def test_archivo_existe_relativa_valida(monkeypatch, tmp_path, ruta):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    (tmp_path / "README.md").write_text("ok", encoding="utf-8")

    assert archivo.existe(ruta) is True


@pytest.mark.parametrize(
    "ruta",
    [
        "/etc/passwd",
        "C:\\Windows\\System32\\drivers\\etc\\hosts",
        "\\\\server\\share\\file.txt",
        "//server/share/file.txt",
        "D:/datos/secret.txt",
    ],
)
def test_archivo_existe_bloquea_absolutas_y_windows_unc(monkeypatch, tmp_path, ruta):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    assert archivo.existe(ruta) is False


@pytest.mark.parametrize(
    "ruta",
    [
        "./../secreto.txt",
        "a/../../secreto.txt",
        "carpeta/../..//secreto.txt",
        "subdir/./.././../secreto.txt",
    ],
)
def test_archivo_existe_bloquea_traversal(monkeypatch, tmp_path, ruta):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    assert archivo.existe(ruta) is False


def test_archivo_existe_solo_acepta_str(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    (tmp_path / "README.md").write_text("ok", encoding="utf-8")
    assert archivo.existe(Path("README.md")) is False
