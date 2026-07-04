from __future__ import annotations

import importlib
from zipfile import ZipFile

import pytest

import pcobra.corelibs.compresion as compresion


def test_import_directo_y_all_presente() -> None:
    modulo = importlib.import_module("pcobra.corelibs.compresion")

    assert modulo is compresion
    assert isinstance(compresion.__all__, list)
    assert "crear_zip" in compresion.__all__
    assert callable(getattr(compresion, "crear_zip"))


def test_crear_listar_y_extraer_zip_con_tmp_path(tmp_path) -> None:
    origen = tmp_path / "origen"
    origen.mkdir()
    archivo = origen / "datos.txt"
    archivo.write_text("contenido", encoding="utf-8")
    zip_path = tmp_path / "salida" / "datos.zip"

    nombres = compresion.crear_zip(zip_path, archivo, base=origen)
    destino = tmp_path / "extraido"
    extraidas = compresion.extraer_zip(zip_path, destino)

    assert nombres == ["datos.txt"]
    assert compresion.listar_zip(zip_path) == ["datos.txt"]
    assert (destino / "datos.txt").read_text(encoding="utf-8") == "contenido"
    assert str(destino / "datos.txt") in extraidas


def test_extraer_zip_rechaza_path_traversal(tmp_path) -> None:
    zip_path = tmp_path / "inseguro.zip"
    with ZipFile(zip_path, "w") as archivo_zip:
        archivo_zip.writestr("../escape.txt", "no")

    with pytest.raises(ValueError):
        compresion.extraer_zip(zip_path, tmp_path / "destino")
