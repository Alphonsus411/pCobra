from __future__ import annotations

from pathlib import Path

import pytest

import pcobra.corelibs.temporal as temporal


def test_import_directo_y_all_presente() -> None:
    assert isinstance(temporal.__all__, list)
    assert "limpiar" in temporal.__all__


def test_archivo_y_directorio_temporal_se_limpian() -> None:
    archivo = Path(temporal.archivo_temporal(prefijo="pcobra-", sufijo=".tmp"))
    directorio = Path(temporal.directorio_temporal(prefijo="pcobra-"))
    try:
        assert archivo.exists()
        assert directorio.is_dir()
    finally:
        assert temporal.limpiar(archivo) is True
        assert temporal.limpiar(directorio) is True

    assert temporal.limpiar(archivo) is False


def test_limpiar_rechaza_ruta_vacia() -> None:
    with pytest.raises(ValueError):
        temporal.limpiar("")
