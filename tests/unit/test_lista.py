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
    assert lista.mapear_aplanado([1, 3], lambda x: range(x)) == [0, 0, 1, 2]

    class Caja:
        def __init__(self, valor):
            self.valor = valor

    cajas = [Caja(1), Caja(2)]
    resultado_cajas = lista.mapear_aplanado(cajas, lambda caja: (caja,))
    assert all(isinstance(elem, Caja) for elem in resultado_cajas)
    assert resultado_cajas[0] is cajas[0]
    assert resultado_cajas[1] is cajas[1]
    assert lista.ventanas([1, 2, 3, 4], 2) == [[1, 2], [2, 3], [3, 4]]
    assert lista.ventanas([1, 2, 3, 4], 3, paso=2, incluir_incompletas=True) == [
        [1, 2, 3],
        [3, 4],
    ]
    assert lista.chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert lista.chunk([1, 2, 3, 4, 5], 2, incluir_incompleto=False) == [[1, 2], [3, 4]]
    assert lista.tomar_mientras((3, 2, 1, 0), lambda x: x > 0) == [3, 2, 1]
    assert lista.descartar_mientras([0, 0, 1, 2], lambda x: x == 0) == [1, 2]
    assert lista.scanear([1, 2, 3], lambda acc, x: acc + x) == [1, 3, 6]
    assert lista.scanear([1, 2, 3], lambda acc, x: acc + x, 0) == [0, 1, 3, 6]
    assert lista.scanear([], lambda acc, x: acc + x, 5) == [5]
    assert lista.pares_consecutivos(["a", "b", "c"]) == [("a", "b"), ("b", "c")]
    with pytest.raises(TypeError):
        lista.tomar_mientras(123, lambda x: x)
    with pytest.raises(TypeError):
        lista.descartar_mientras(123, lambda x: x)
    with pytest.raises(TypeError):
        lista.scanear([1, 2], "no callable")
    with pytest.raises(TypeError):
        lista.mapear_aplanado([1], lambda _: 42)
    def reventar(acc, x):  # pragma: no cover - auxiliar para excepciones
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        lista.scanear([1, 2], reventar)
    with pytest.raises(ValueError):
        lista.ventanas(datos, 0)
    with pytest.raises(ValueError):
        lista.chunk(datos, 0)

