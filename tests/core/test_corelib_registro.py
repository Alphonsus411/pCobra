from __future__ import annotations

import importlib
import logging

import pytest

import pcobra.corelibs.registro as registro


def test_import_directo_y_all_presente() -> None:
    modulo = importlib.import_module("pcobra.corelibs.registro")

    assert modulo is registro
    assert isinstance(registro.__all__, list)
    assert "configurar" in registro.__all__
    assert callable(getattr(registro, "configurar"))


def test_configurar_registro_en_archivo_temporal(tmp_path) -> None:
    destino = tmp_path / "cobra.log"
    logger = registro.configurar(nivel="INFO", destino=destino)

    registro.info("mensaje portable")
    for handler in logger.handlers:
        handler.flush()

    assert logger.level == logging.INFO
    assert "INFO:pcobra.registro:mensaje portable" in destino.read_text(encoding="utf-8")


def test_configurar_nivel_invalido_lanza_value_error() -> None:
    with pytest.raises(ValueError):
        registro.configurar(nivel="NO_EXISTE")
