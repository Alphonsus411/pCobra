from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from pcobra.standard_library import datos as datos_mod
from pcobra.standard_library.datos import (
    agrupar_y_resumir,
    a_listas,
    combinar_tablas,
    de_listas,
    describir,
    desplegar_tabla,
    escribir_excel,
    filtrar,
    leer_csv,
    leer_excel,
    leer_json,
    ordenar_tabla,
    pivotar_tabla,
    rellenar_nulos,
    seleccionar_columnas,
)


def _tabla_base() -> list[dict[str, object]]:
    return [
        {"categoria": "A", "valor": 10, "etiqueta": "foo"},
        {"categoria": "A", "valor": 5, "etiqueta": "bar"},
        {"categoria": "B", "valor": 3, "etiqueta": "baz"},
    ]


@pytest.fixture
def tabla_clientes() -> list[dict[str, object]]:
    return [
        {"cliente_id": 1, "region": "norte"},
        {"cliente_id": 2, "region": "sur"},
        {"cliente_id": 3, "region": "norte"},
    ]


@pytest.fixture
def tabla_pedidos() -> list[dict[str, object | None]]:
    return [
        {"cliente": 1, "mes": "enero", "monto": 120.0, "unidades": 5},
        {"cliente": 1, "mes": None, "monto": None, "unidades": 2},
        {"cliente": 2, "mes": "enero", "monto": 80.0, "unidades": 3},
        {"cliente": 4, "mes": "enero", "monto": 60.0, "unidades": 1},
    ]


@pytest.fixture
def tabla_metricas() -> list[dict[str, object | None]]:
    return [
        {"region": "norte", "mes": "enero", "monto": 100, "descuento": 5},
        {"region": "norte", "mes": "enero", "monto": 40, "descuento": 2},
        {"region": "norte", "mes": "febrero", "monto": 50, "descuento": None},
        {"region": "sur", "mes": "enero", "monto": 70, "descuento": 1},
        {"region": "sur", "mes": "febrero", "monto": 30, "descuento": 3},
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


def test_ordenar_tabla_multiple(tabla_pedidos: list[dict[str, object | None]]):
    ordenado = ordenar_tabla(tabla_pedidos, por=["cliente", "unidades"], ascendente=[True, False])
    esperado = [
        {"cliente": 1, "mes": "enero", "monto": 120.0, "unidades": 5},
        {"cliente": 1, "mes": None, "monto": None, "unidades": 2},
        {"cliente": 2, "mes": "enero", "monto": 80.0, "unidades": 3},
        {"cliente": 4, "mes": "enero", "monto": 60.0, "unidades": 1},
    ]
    assert ordenado == esperado


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


def test_escribir_y_leer_excel(tmp_path: Path):
    pytest.importorskip("openpyxl")
    tabla = _tabla_base()
    ruta = tmp_path / "salida" / "tabla.xlsx"
    escribir_excel(tabla, ruta, hoja="Datos", engine="openpyxl")
    assert ruta.exists()
    leidos = leer_excel(ruta, hoja="Datos", engine="openpyxl")
    assert leidos == tabla


def test_leer_excel_sin_encabezado(tmp_path: Path):
    pytest.importorskip("openpyxl")
    ruta = tmp_path / "sin_encabezado.xlsx"
    pd.DataFrame([[1, "A"], [2, "B"]]).to_excel(
        ruta,
        header=False,
        index=False,
        engine="openpyxl",
    )
    datos = leer_excel(ruta, encabezado=None, engine="openpyxl")
    assert datos == [{0: 1, 1: "A"}, {0: 2, 1: "B"}]


def test_combinar_tablas_inner(tabla_clientes, tabla_pedidos):
    combinado = combinar_tablas(
        tabla_clientes,
        tabla_pedidos,
        claves=("cliente_id", "cliente"),
        tipo="inner",
    )
    clientes_presentes = {fila["cliente_id"] for fila in combinado}
    assert clientes_presentes == {1, 2}
    assert all("mes" in fila and "monto" in fila for fila in combinado)


def test_combinar_tablas_outer(tabla_clientes, tabla_pedidos):
    combinado = combinar_tablas(
        tabla_clientes,
        tabla_pedidos,
        claves={"izquierda": "cliente_id", "derecha": "cliente"},
        tipo="outer",
    )
    # Se conservan clientes sin pedidos y pedidos sin cliente registrado.
    from collections import Counter

    ids = Counter((fila.get("cliente_id"), fila.get("cliente")) for fila in combinado)
    assert ids == Counter({(1, 1): 2, (2, 2): 1, (3, None): 1, (None, 4): 1})


def test_rellenar_nulos_por_columna(tabla_pedidos):
    rellenos = rellenar_nulos(tabla_pedidos, {"monto": 0.0, "mes": "sin datos"})
    assert any(fila["mes"] == "sin datos" for fila in rellenos)
    assert any(fila["monto"] == 0.0 for fila in rellenos)
    # Las columnas no reemplazadas conservan sus valores originales.
    assert rellenos[0]["unidades"] == 5


def test_desplegar_tabla_con_varias_columnas(tabla_metricas):
    desplegada = desplegar_tabla(
        tabla_metricas,
        identificadores=["region", "mes"],
        valores=["monto", "descuento"],
        var_name="metrica",
        value_name="valor",
    )
    assert len(desplegada) == len(tabla_metricas) * 2
    assert desplegada[0] == {
        "region": "norte",
        "mes": "enero",
        "metrica": "monto",
        "valor": 100,
    }
    registro_descuento = next(
        fila
        for fila in desplegada
        if fila["region"] == "norte" and fila["mes"] == "febrero" and fila["metrica"] == "descuento"
    )
    assert registro_descuento["valor"] is None


def test_desplegar_tabla_sin_especificar_valores():
    datos = [
        {"id": 1, "col_a": 10, "col_b": None},
        {"id": 2, "col_a": 20, "col_b": 30},
    ]
    desplegada = desplegar_tabla(datos, identificadores="id")
    assert desplegada == [
        {"id": 1, "variable": "col_a", "value": 10},
        {"id": 2, "variable": "col_a", "value": 20},
        {"id": 1, "variable": "col_b", "value": None},
        {"id": 2, "variable": "col_b", "value": 30},
    ]


def test_pivotar_tabla_multiple_metricas(tabla_metricas):
    pivotado = pivotar_tabla(
        tabla_metricas,
        index="region",
        columnas="mes",
        valores=["monto", "descuento"],
        agregacion={"monto": ["sum", "mean"], "descuento": "mean"},
    )
    regiones = {fila["region"] for fila in pivotado}
    assert regiones == {"norte", "sur"}
    # Se generan columnas con agregaciones múltiples y valores saneados.
    columnas_generadas = set(pivotado[0].keys())
    assert {
        "region",
        "monto_sum_enero",
        "monto_mean_febrero",
        "descuento_mean_enero",
    }.issubset(columnas_generadas)


def test_desde_modulo_publico():
    # Asegura que las re-exportaciones incluyan anotaciones y funciones activas.
    assert hasattr(datos_mod, "leer_csv")
    assert callable(datos_mod.leer_csv)
