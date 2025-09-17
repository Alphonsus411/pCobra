import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import standard_library.lista as lista


def test_lista():
    datos = [1, 2, 3]
    assert lista.cabeza(datos) == 1
    assert lista.cola(datos) == [2, 3]
    assert lista.longitud(datos) == 3
    assert lista.combinar([1], [2, 3]) == [1, 2, 3]
    resultados, errores = lista.mapear_seguro(
        datos, lambda x: x if x != 2 else 1 / 0, valor_por_defecto=0
    )
    assert resultados == [1, 0, 3]
    assert len(errores) == 1 and errores[0][0] == 2
    assert lista.ventanas([1, 2, 3, 4], 2) == [[1, 2], [2, 3], [3, 4]]
    assert lista.ventanas([1, 2, 3, 4], 3, paso=2, incluir_incompletas=True) == [
        [1, 2, 3],
        [3, 4],
    ]
    assert lista.chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert lista.chunk([1, 2, 3, 4, 5], 2, incluir_incompleto=False) == [[1, 2], [3, 4]]
    with pytest.raises(ValueError):
        lista.ventanas(datos, 0)
    with pytest.raises(ValueError):
        lista.chunk(datos, 0)

