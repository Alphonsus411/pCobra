from __future__ import annotations

import pytest

from pcobra.core.holobits.graficar import (
    _HOLOBIT_SDK_ERROR,
    _to_sdk_holobit,
    graficar,
)
from pcobra.core.holobits.holobit import Holobit
from pcobra.core.holobits.proyeccion import proyectar
from pcobra.core.holobits.transformacion import transformar


def test_to_sdk_holobit_builds_stub_object_even_without_optional_sdk():
    sdk_hb = _to_sdk_holobit(Holobit([1, 2, 3]))

    assert hasattr(sdk_hb, "quarks")
    assert hasattr(sdk_hb, "antiquarks")
    assert len(sdk_hb.quarks) == 6
    assert len(sdk_hb.antiquarks) == 6


@pytest.mark.skipif(
    _HOLOBIT_SDK_ERROR is None,
    reason="Solo aplica cuando holobit_sdk no está instalado.",
)
@pytest.mark.parametrize(
    ("funcion", "args"),
    (
        (graficar, (Holobit([1, 2, 3]),)),
        (proyectar, (Holobit([1, 2, 3]), "2d")),
        (transformar, (Holobit([1, 2, 3]), "rotar", "z", 45)),
    ),
)
def test_holobit_sdk_fallback_fails_gracefully_when_sdk_is_missing(funcion, args):
    with pytest.raises(ModuleNotFoundError, match="holobit_sdk"):
        funcion(*args)
