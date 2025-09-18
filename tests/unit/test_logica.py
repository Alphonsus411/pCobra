import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pytest

import standard_library.logica as logica


def test_logica_tablas_de_verdad():
    casos = [
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    ]
    for a, b in casos:
        assert logica.conjuncion(a, b) is (a and b)
        assert logica.disyuncion(a, b) is (a or b)
        assert logica.negacion(a) is (not a)
        assert logica.xor(a, b) is ((a and not b) or (not a and b))
        assert logica.nand(a, b) is (not (a and b))
        assert logica.nor(a, b) is (not (a or b))
        assert logica.implica(a, b) is ((not a) or b)
        assert logica.equivale(a, b) is (a is b)

    assert logica.xor_multiple(True, False, True) is False
    assert logica.xor_multiple(True, True, False, False) is False
    assert logica.xor_multiple(True, False, False, False) is True


def test_logica_colecciones():
    assert logica.todas([True, True, True]) is True
    assert logica.todas([True, False]) is False
    assert logica.alguna([False, False, True]) is True
    assert logica.alguna([False, False]) is False


def test_logica_valida_entradas():
    with pytest.raises(TypeError):
        logica.conjuncion(1, True)
    with pytest.raises(TypeError):
        logica.disyuncion(True, "no bool")
    with pytest.raises(TypeError):
        logica.negacion("no bool")
    with pytest.raises(ValueError):
        logica.xor_multiple(True)
    with pytest.raises(TypeError):
        logica.xor_multiple(True, 0)
    with pytest.raises(TypeError):
        logica.todas([True, 1])
    with pytest.raises(TypeError):
        logica.alguna([False, None])

