from types import SimpleNamespace
from unittest.mock import patch

import pytest

from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.semantic_validators import PrimitivaPeligrosaError
from pcobra.core.usar_symbol_policy import validate_usar_symbol_metadata


def test_metadata_usar_debug_tolera_claves_heterogeneas_en_metadata_corrupta():
    interp = InterpretadorCobra()
    interp._usar_symbol_metadata = {"existe": {}}
    interp._validador = SimpleNamespace(_metadata_simbolos_usar={"existe": {}, 1: {}})

    with patch("pcobra.core.interpreter._usar_detalle_habilitado", return_value=True):
        with pytest.raises(PrimitivaPeligrosaError) as err:
            interp._asegurar_metadata_usar_sincronizada(etapa="test")

    mensaje = str(err.value)
    assert "codigo_interno='missing_keys'" in mensaje
    assert "detalle_debug=" in mensaje
    assert "received_keys" in mensaje
    assert "validate_usar_symbol_metadata" in mensaje


def test_metadata_usar_debug_helper_ordena_claves_anidadas_heterogeneas():
    with patch("pcobra.core.interpreter._usar_detalle_habilitado", return_value=True):
        detalle = InterpretadorCobra._detalle_debug_metadata_usar(
            symbol="existe",
            expected_keys={"module", 1},
            received_keys={"module", 2},
        )

    assert "detalle_debug=" in detalle
    assert "expected_keys" in detalle
    assert "received_keys" in detalle
    assert "validate_usar_symbol_metadata" in detalle


def test_validador_metadata_usar_rechaza_claves_heterogeneas_sin_typeerror():
    metadata = {
        "origin_kind": "usar",
        "module": "archivo",
        "symbol": "existe",
        "sanitized": True,
        "public_api": True,
        "backend_exposed": False,
        "callable": True,
        1: "clave-corrupta",
    }

    with pytest.raises(ValueError, match="claves inesperadas críticas"):
        validate_usar_symbol_metadata("existe", metadata)
