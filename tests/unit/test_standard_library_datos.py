from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import pcobra.standard_library.datos as datos_mod
from pcobra.standard_library.datos import (
    agrupar_y_resumir,
    a_listas,
    calcular_percentiles,
    correlacion_pearson,
    correlacion_spearman,
    combinar_tablas,
    de_listas,
    describir,
    desplegar_tabla,
    escribir_csv,
    escribir_excel,
    escribir_feather,
    escribir_json,
    escribir_parquet,
    filtrar,
    matriz_covarianza,
    mutar_columna,
    separar_columna,
    leer_csv,
    leer_excel,
    leer_feather,
    leer_json,
    leer_parquet,
    pivotar_ancho,
    pivotar_largo,
    ordenar_tabla,
    pivotar_tabla,
    tabla_cruzada,
    rellenar_nulos,
    resumen_rapido,
    unir_columnas,
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


@pytest.fixture
def tabla_estadistica() -> list[dict[str, object | None]]:
    return [
        {
            "ventas": 10.0,
            "costos": 15.0,
            "unidades": 3,
            "fecha": pd.Timestamp("2024-01-01"),
            "segmento": "A",
        },
        {
            "ventas": 20.0,
            "costos": 30.0,
            "unidades": 6,
            "fecha": pd.Timestamp("2024-01-02"),
            "segmento": "A",
        },
        {
            "ventas": 30.0,
            "costos": 45.0,
            "unidades": None,
            "fecha": pd.Timestamp("2024-01-03"),
            "segmento": "B",
        },
        {
            "ventas": 40.0,
            "costos": None,
            "unidades": 12,
            "fecha": None,
            "segmento": "B",
        },
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


def test_mutar_columna_crear_y_actualizar():
    tabla = _tabla_base()
    con_nueva = mutar_columna(tabla, "valor_doble", lambda fila: fila["valor"] * 2)
    assert [fila["valor_doble"] for fila in con_nueva] == [20, 10, 6]

    mayusculas = mutar_columna(
        con_nueva,
        "etiqueta",
        lambda fila: str(fila["etiqueta"]).upper(),
        crear_si_no_existe=False,
    )
    assert [fila["etiqueta"] for fila in mayusculas] == ["FOO", "BAR", "BAZ"]


def test_separar_columna_delimitador_personalizado():
    datos = [
        {"codigo": "A-01", "extra": 1},
        {"codigo": "B-02", "extra": 2},
        {"codigo": None, "extra": 3},
    ]

    resultado = separar_columna(
        datos,
        "codigo",
        en=["serie", "numero"],
        separador="-",
        relleno="sin_dato",
        eliminar_original=False,
    )

    assert resultado[0]["serie"] == "A"
    assert resultado[0]["numero"] == "01"
    assert resultado[2]["serie"] == "sin_dato"
    assert resultado[2]["numero"] == "sin_dato"

    solo_completos = separar_columna(
        datos,
        "codigo",
        en=["serie", "numero"],
        separador="-",
        descartar_nulos=True,
    )

    assert len(solo_completos) == 2
    assert all("serie" in fila and "numero" in fila for fila in solo_completos)


def test_unir_columnas_control_nulos():
    datos = [
        {"nombre": "Ada", "zona": "Norte", "nivel": None},
        {"nombre": "Grace", "zona": None, "nivel": "A"},
        {"nombre": None, "zona": None, "nivel": None},
    ]

    unidos = unir_columnas(
        datos,
        ["nombre", "zona", "nivel"],
        "etiqueta",
        separador="/",
        omitir_nulos=True,
        eliminar_original=False,
    )

    assert unidos[0]["etiqueta"] == "Ada/Norte"
    assert unidos[1]["etiqueta"] == "Grace/A"
    assert unidos[2]["etiqueta"] is None

    unidos_con_relleno = unir_columnas(
        datos,
        ["nombre", "zona"],
        "nombre_zona",
        separador=" - ",
        omitir_nulos=False,
        relleno="sin dato",
        eliminar_original=False,
    )

    assert unidos_con_relleno[0]["nombre_zona"] == "Ada - Norte"
    assert unidos_con_relleno[1]["nombre_zona"] == "Grace - sin dato"
    assert unidos_con_relleno[2]["nombre_zona"] == "sin dato - sin dato"


def test_tabla_cruzada_conteo_simple():
    datos = [
        {"region": "norte", "genero": "F"},
        {"region": "norte", "genero": "M"},
        {"region": "sur", "genero": "F"},
    ]

    tabla = tabla_cruzada(datos, "region", "genero")

    assert tabla == [
        {"region": "norte", "F": 1, "M": 1},
        {"region": "sur", "F": 1, "M": 0},
    ]


def test_tabla_cruzada_agregacion_personalizada():
    datos = [
        {"region": "norte", "mes": "enero", "monto": 100},
        {"region": "norte", "mes": "enero", "monto": 50},
        {"region": "norte", "mes": "febrero", "monto": 20},
        {"region": "sur", "mes": "enero", "monto": 70},
        {"region": "sur", "mes": "febrero", "monto": 30},
    ]

    tabla = tabla_cruzada(
        datos,
        "region",
        "mes",
        valores="monto",
        aggfunc="sum",
    )

    assert tabla == [
        {"region": "norte", "enero": 150, "febrero": 20},
        {"region": "sur", "enero": 70, "febrero": 30},
    ]


def test_tabla_cruzada_normalizacion_filas_columnas():
    datos = [
        {"segmento": "A", "estado": "activo"},
        {"segmento": "A", "estado": "activo"},
        {"segmento": "A", "estado": "inactivo"},
        {"segmento": "B", "estado": "activo"},
    ]

    por_filas = tabla_cruzada(datos, "segmento", "estado", normalizar="filas")
    assert por_filas[0]["activo"] == pytest.approx(2 / 3)
    assert por_filas[0]["inactivo"] == pytest.approx(1 / 3)
    assert por_filas[1]["activo"] == pytest.approx(1.0)
    assert por_filas[1]["inactivo"] == pytest.approx(0.0)

    por_columnas = tabla_cruzada(datos, "segmento", "estado", normalizar="columnas")
    assert por_columnas[0]["activo"] == pytest.approx(2 / 3)
    assert por_columnas[1]["activo"] == pytest.approx(1 / 3)
    assert por_columnas[0]["inactivo"] == pytest.approx(1.0)
    assert por_columnas[1]["inactivo"] == pytest.approx(0.0)


def test_mutar_columna_exige_existente():
    with pytest.raises(KeyError):
        mutar_columna(_tabla_base(), "nueva", lambda fila: fila["valor"], crear_si_no_existe=False)


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


def test_pivotar_ancho_rellena_faltantes():
    datos = [
        {"id": 1, "mes": "enero", "monto": 10},
        {"id": 1, "mes": "febrero", "monto": 12},
        {"id": 2, "mes": "enero", "monto": 5},
    ]
    ancho = pivotar_ancho(
        datos,
        id_columnas="id",
        nombres_desde="mes",
        valores_desde="monto",
        valores_relleno=0,
    )
    assert ancho == [
        {"id": 1, "monto_enero": 10, "monto_febrero": 12},
        {"id": 2, "monto_enero": 5, "monto_febrero": 0},
    ]


def test_pivotar_largo_elimina_nulos():
    datos = [
        {"id": 1, "enero": 10, "febrero": None},
        {"id": 2, "enero": 5, "febrero": 7},
    ]
    largo = pivotar_largo(
        datos,
        columnas=["enero", "febrero"],
        id_columnas="id",
        nombres_a="mes",
        valores_a="monto",
        eliminar_nulos=True,
    )
    assert largo == [
        {"id": 1, "mes": "enero", "monto": 10},
        {"id": 2, "mes": "enero", "monto": 5},
        {"id": 2, "mes": "febrero", "monto": 7},
    ]


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


def test_correlaciones_controladas(tabla_estadistica: list[dict[str, object | None]]):
    pearson = correlacion_pearson(tabla_estadistica, columnas=["ventas", "costos", "unidades"])
    assert pearson["ventas"]["costos"] == pytest.approx(1.0)
    assert pearson["ventas"]["unidades"] == pytest.approx(1.0)
    assert pearson["ventas"]["ventas"] == pytest.approx(1.0)

    spearman = correlacion_spearman(tabla_estadistica)
    assert spearman["ventas"]["costos"] == pytest.approx(1.0)
    assert spearman["ventas"]["unidades"] == pytest.approx(1.0)

    with pytest.raises(KeyError):
        correlacion_pearson(tabla_estadistica, columnas=["ventas", "faltante"])


def test_correlacion_sin_numericos():
    datos = [{"categoria": "A"}, {"categoria": "B"}]
    with pytest.raises(ValueError):
        correlacion_pearson(datos)


def test_matriz_covarianza(tabla_estadistica: list[dict[str, object | None]]):
    matriz = matriz_covarianza(tabla_estadistica, columnas=["ventas", "costos", "unidades"])
    assert matriz["ventas"]["costos"] == pytest.approx(150.0)
    assert matriz["ventas"]["unidades"] == pytest.approx(70.0)
    assert matriz["costos"]["unidades"] == pytest.approx(22.5)


def test_percentiles_por_defecto(tabla_estadistica: list[dict[str, object | None]]):
    percentiles = calcular_percentiles(tabla_estadistica)
    assert percentiles["ventas"]["p25"] == pytest.approx(17.5)
    assert percentiles["ventas"]["p50"] == pytest.approx(25.0)
    assert percentiles["ventas"]["p75"] == pytest.approx(32.5)
    assert percentiles["costos"]["p75"] == pytest.approx(37.5)
    assert percentiles["unidades"]["p75"] == pytest.approx(9.0)

    with pytest.raises(ValueError):
        calcular_percentiles(tabla_estadistica, percentiles=())
    with pytest.raises(ValueError):
        calcular_percentiles(tabla_estadistica, percentiles=[-0.1, 0.5])


def test_resumen_rapido(tabla_estadistica: list[dict[str, object | None]]):
    resumen = resumen_rapido(tabla_estadistica)
    assert len(resumen) == 5
    por_columna = {item["columna"]: item for item in resumen}

    assert por_columna["ventas"]["media"] == pytest.approx(25.0)
    assert por_columna["costos"]["nulos"] == 1
    assert por_columna["fecha"]["min"] == "2024-01-01T00:00:00"
    assert por_columna["segmento"]["ejemplo"] == "A"


def test_leer_csv_y_json(tmp_path: Path):
    csv_path = tmp_path / "datos.csv"
    csv_path.write_text("categoria,valor\nA,10\nB,\n", encoding="utf-8")
    datos_csv = leer_csv(csv_path)
    assert datos_csv == [{"categoria": "A", "valor": 10}, {"categoria": "B", "valor": None}]

    json_path = tmp_path / "datos.json"
    json_path.write_text('[{"categoria": "C", "valor": 7}]', encoding="utf-8")
    datos_json = leer_json(json_path)
    assert datos_json == [{"categoria": "C", "valor": 7}]


def test_escribir_csv(tmp_path: Path):
    tabla = _tabla_base()
    destino = tmp_path / "reporte" / "datos.csv"
    escribir_csv(tabla, destino, separador=";", encoding="utf-8")
    escribir_csv(
        [{"categoria": "C", "valor": None}],
        destino,
        separador=";",
        encoding="utf-8",
        aniadir=True,
    )
    leidos = leer_csv(destino, separador=";")
    assert leidos == [
        {"categoria": "A", "valor": 10, "etiqueta": "foo"},
        {"categoria": "A", "valor": 5, "etiqueta": "bar"},
        {"categoria": "B", "valor": 3, "etiqueta": "baz"},
        {"categoria": "C", "valor": None, "etiqueta": None},
    ]


def test_escribir_json(tmp_path: Path):
    tabla = _tabla_base()
    ruta_json = tmp_path / "datos.json"
    escribir_json(tabla, ruta_json, indent=2)
    assert leer_json(ruta_json) == tabla

    ruta_jsonl = tmp_path / "datos.jsonl"
    escribir_json(tabla[:2], ruta_jsonl, lineas=True)
    escribir_json([{"categoria": "C", "valor": None}], ruta_jsonl, lineas=True, aniadir=True)
    assert leer_json(ruta_jsonl, lineas=True) == [
        {"categoria": "A", "valor": 10, "etiqueta": "foo"},
        {"categoria": "A", "valor": 5, "etiqueta": "bar"},
        {"categoria": "C", "valor": None, "etiqueta": None},
    ]


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


def test_escribir_y_leer_parquet(tmp_path: Path):
    pytest.importorskip("pyarrow")
    tabla = _tabla_base()
    ruta = tmp_path / "tabla.parquet"
    escribir_parquet(tabla, ruta, engine="pyarrow")
    assert ruta.exists()
    leidos = leer_parquet(ruta, engine="pyarrow")
    assert leidos == tabla


def test_parquet_sin_dependencias(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(datos_mod, "_modulo_disponible", lambda _nombre: False)
    with pytest.raises(ValueError, match="Instala 'pyarrow' o 'fastparquet'"):
        leer_parquet(tmp_path / "faltante.parquet")


def test_escribir_y_leer_feather(tmp_path: Path):
    pytest.importorskip("pyarrow")
    tabla = _tabla_base()
    ruta = tmp_path / "tabla.feather"
    escribir_feather(tabla, ruta)
    assert ruta.exists()
    leidos = leer_feather(ruta)
    assert leidos == tabla


def test_feather_sin_pyarrow(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(datos_mod, "_modulo_disponible", lambda _nombre: False)
    with pytest.raises(ValueError, match="instala el paquete opcional 'pyarrow'"):
        escribir_feather(_tabla_base(), tmp_path / "salida.feather")


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
