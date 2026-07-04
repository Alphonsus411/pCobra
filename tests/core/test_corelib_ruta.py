from __future__ import annotations

import pytest

import pcobra.corelibs.ruta as ruta


def test_import_directo_y_all_presente() -> None:
    assert isinstance(ruta.__all__, list)
    assert "unir" in ruta.__all__


def test_unir_y_relativa_multiplataforma(tmp_path) -> None:
    archivo = tmp_path / "datos" / "entrada.txt"
    archivo.parent.mkdir()
    archivo.write_text("ok", encoding="utf-8")

    construida = ruta.unir(tmp_path, "datos", "entrada.txt")

    assert ruta.existe(construida) is True
    assert ruta.nombre(construida) == "entrada.txt"
    assert ruta.extension(construida) == ".txt"
    assert ruta.relativa(construida, tmp_path) == ruta.unir("datos", "entrada.txt")


def test_unir_rechaza_partes_vacias() -> None:
    with pytest.raises(ValueError):
        ruta.unir()
