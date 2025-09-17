from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from pcobra.standard_library import datos as datos_mod
from pcobra.standard_library.datos import (
    agrupar_y_resumir,
    a_listas,
    de_listas,
    describir,
    filtrar,
    leer_csv,
    leer_json,
    seleccionar_columnas,
)


def _tabla_base() -> list[dict[str, object]]:
    return [
        {"categoria": "A", "valor": 10, "etiqueta": "foo"},
        {"categoria": "A", "valor": 5, "etiqueta": "bar"},
        {"categoria": "B", "valor": 3, "etiqueta": "baz"},
    ]


def test_a_listas_y_de_listas_bidireccional():
    tabla = _tabla_base()
    columnas = a_listas(tabla)
    reconstruido = de_listas(columnas)
    assert reconstruido == tabla


def test_de_listas_columnas_inconsistentes():
    with pytest.raises(ValueError):
        de_listas({"a": [1, 2], "b": [3]})


def test_seleccionar_columnas_y_filtrar():
    tabla = _tabla_base()
    seleccion = seleccionar_columnas(tabla, ["categoria", "valor"])
    assert all(set(fila.keys()) == {"categoria", "valor"} for fila in seleccion)
    filtrado = filtrar(seleccion, lambda fila: fila["valor"] > 5)
    assert filtrado == [{"categoria": "A", "valor": 10}]


def test_filtrar_condicion_erronea():
    tabla = _tabla_base()

    def condicion(_fila: dict[str, object]) -> bool:
        raise RuntimeError("fallo")

    with pytest.raises(ValueError):
        filtrar(tabla, condicion)


def test_seleccionar_columnas_inexistentes():
    with pytest.raises(KeyError):
        seleccionar_columnas(_tabla_base(), ["id"])


def test_agrupar_y_resumir():
    tabla = _tabla_base()
    resultado = agrupar_y_resumir(tabla, por=["categoria"], agregaciones={"valor": "sum"})
    esperado = [
        {"categoria": "A", "valor_sum": 15},
        {"categoria": "B", "valor_sum": 3},
    ]
    assert resultado == esperado


def test_describir_contiene_metricas():
    df = pd.DataFrame(_tabla_base())
    resumen = describir(df)
    assert "valor" in resumen
    assert "mean" in resumen["valor"]
    assert resumen["valor"]["mean"] == pytest.approx(6.0)


def test_leer_csv_y_json(tmp_path: Path):
    csv_path = tmp_path / "datos.csv"
    csv_path.write_text("categoria,valor\nA,10\nB,\n", encoding="utf-8")
    datos_csv = leer_csv(csv_path)
    assert datos_csv == [{"categoria": "A", "valor": 10}, {"categoria": "B", "valor": None}]

    json_path = tmp_path / "datos.json"
    json_path.write_text('[{"categoria": "C", "valor": 7}]', encoding="utf-8")
    datos_json = leer_json(json_path)
    assert datos_json == [{"categoria": "C", "valor": 7}]


def test_leer_csv_error(tmp_path: Path):
    csv_path = tmp_path / "datos.csv"
    csv_path.write_text('valor\n"1', encoding="utf-8")
    with pytest.raises(ValueError):
        leer_csv(csv_path)


def test_desde_modulo_publico():
    # Asegura que las re-exportaciones incluyan anotaciones y funciones activas.
    assert hasattr(datos_mod, "leer_csv")
    assert callable(datos_mod.leer_csv)
