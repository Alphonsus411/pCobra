import asyncio
import math
import operator
import os
import random
import statistics as stats
import sys
from collections import OrderedDict
from datetime import datetime
from types import ModuleType
from unittest.mock import MagicMock, patch

import numpy as np

import pytest

sys.modules.setdefault("yaml", ModuleType("yaml"))
sys.modules.setdefault("httpx", ModuleType("httpx"))

import core.ast_nodes as core_ast_nodes

sys.modules.setdefault("cobra.core.ast_nodes", core_ast_nodes)

import pcobra.corelibs as core
import pcobra.corelibs.sistema as core_sistema
import pcobra.corelibs.tiempo as core_tiempo
from cobra.transpilers.import_helper import get_standard_imports
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from core.ast_nodes import NodoLlamadaFuncion, NodoValor

IMPORTS_PY = get_standard_imports("python")
IMPORTS_JS = "".join(f"{line}\n" for line in get_standard_imports("js"))


def test_texto_funcs():
    assert core.mayusculas("hola") == "HOLA"
    assert core.minusculas("HOLA") == "hola"
    assert core.capitalizar("cobra") == "Cobra"
    assert core.capitalizar("") == ""
    assert core.titulo("árbol de navidad") == "Árbol De Navidad"
    assert core.intercambiar_mayusculas("ÁRBOL y cobra") == "árbol Y COBRA"
    assert core.invertir("abc") == "cba"
    assert core.concatenar("a", "b") == "ab"
    assert core.es_alfabetico("Árbol") is True
    assert core.es_alfabetico("cobra123") is False
    assert core.es_alfa_numerico("Cobra123") is True
    assert core.es_alfa_numerico("cobra!") is False
    assert core.es_decimal("１２３") is True
    assert core.es_decimal("四") is False
    assert core.es_numerico("¾") is True
    assert core.es_numerico("Ⅷ⅓") is True
    assert core.es_numerico("texto") is False
    assert core.es_identificador("variable_1") is True
    assert core.es_identificador("1variable") is False
    assert core.es_identificador("nombre-apellido") is False
    assert core.es_imprimible("texto con espacios") is True
    assert core.es_imprimible("línea\n") is False
    assert core.es_ascii("ASCII") is True
    assert core.es_ascii("á") is False
    assert core.es_mayusculas("TEXTO") is True
    assert core.es_mayusculas("123") is False
    assert core.es_mayusculas("Texto") is False
    assert core.es_minusculas("texto") is True
    assert core.es_minusculas("texto!") is True
    assert core.es_minusculas("Texto") is False
    assert core.es_minusculas("123") is False
    assert core.es_titulo("Canción De Cuna") is True
    assert core.es_titulo("Canción de cuna") is False
    assert core.es_espacio(" \t\u2009") is True
    assert core.es_espacio(" ") is True
    assert core.es_espacio("") is False
    assert core.es_espacio("texto") is False
    assert core.es_digito("１２３") is True
    assert core.es_digito("Ⅻ") is False
    assert core.quitar_espacios("  hola  ") == "hola"
    assert core.quitar_espacios("--hola--", modo="derecha", caracteres="-") == "--hola"
    with pytest.raises(ValueError):
        core.quitar_espacios("hola", modo="otro")
    assert core.dividir("  hola   mundo  ") == ["hola", "mundo"]
    assert core.dividir("a,b,c", ",", 1) == ["a", "b,c"]
    assert core.dividir_derecha("uno-dos-tres", "-", 1) == ["uno-dos", "tres"]
    assert core.dividir_derecha("  α  β  γ  ", None, 1) == ["  α  β", "γ"]
    with pytest.raises(ValueError):
        core.dividir_derecha("abc", "")
    assert core.subcadena_antes("uno-dos", "-") == "uno"
    assert core.subcadena_despues("uno-dos", "-") == "dos"
    assert core.subcadena_antes_ultima("uno-dos-tres", "-") == "uno-dos"
    assert core.subcadena_despues_ultima("uno-dos-tres", "-") == "tres"
    assert core.subcadena_antes("texto", "|") == "texto"
    assert core.subcadena_despues("texto", "|") == "texto"
    assert core.subcadena_antes("texto", "|", "N/A") == "N/A"
    assert core.subcadena_despues("texto", "|", "N/A") == "N/A"
    assert core.subcadena_antes_ultima("texto", "|", "N/A") == "N/A"
    assert core.subcadena_despues_ultima("texto", "|", "N/A") == "N/A"
    cadena = "毒🐍🍎"
    assert core.subcadena_antes(cadena, "🐍") == "毒"
    assert core.subcadena_despues(cadena, "🐍") == "🍎"
    assert core.subcadena_antes_ultima(cadena, "🐍") == "毒"
    assert core.subcadena_despues_ultima(cadena, "🐍") == "🍎"
    assert core.subcadena_antes("abc", "") == ""
    assert core.subcadena_despues("abc", "") == "abc"
    assert core.subcadena_antes_ultima("abc", "") == "abc"
    assert core.subcadena_despues_ultima("abc", "") == ""
    assert core.unir("-", ["1", 2, "3"]) == "1-2-3"
    assert core.reemplazar("banana", "na", "NA", 1) == "baNAna"
    assert core.reemplazar("abc", "", "-", 2) == "-a-bc"
    assert core.empieza_con("cobral", ("co", "za")) is True
    assert core.termina_con("cobral", ("co", "al")) is True
    assert core.incluye("hola", "ol") is True
    assert core.quitar_prefijo("prefijo", "pre") == "fijo"
    assert core.quitar_prefijo("prefijo", "prE") == "prefijo"
    assert core.quitar_sufijo("archivo.tmp", ".tmp") == "archivo"
    assert core.quitar_sufijo("archivo.tmp", ".tm") == "archivo.tmp"
    assert core.prefijo_comun("mañana", "Mañanita", ignorar_mayusculas=True) == "mañan"
    assert core.prefijo_comun(
        "Canción",
        "cancio\u0301n",
        ignorar_mayusculas=True,
        normalizar="NFC",
    ) == "Canción"
    assert core.prefijo_comun("東京タワー", "東京ドーム") == "東京"
    assert core.sufijo_comun("astronomía", "economía") == "onomía"
    assert core.sufijo_comun(
        "Αθηναϊκό",
        "Λαϊκό",
        ignorar_mayusculas=True,
        normalizar="NFC",
    ) == "αϊκό"
    assert core.sufijo_comun("hola", "mundo") == ""
    assert core.dividir_lineas("uno\r\ndos\n") == ["uno", "dos"]
    assert core.dividir_lineas("uno\r\ndos\n", conservar_delimitadores=True) == [
        "uno\r\n",
        "dos\n",
    ]
    assert core.dividir_lineas("") == []
    assert core.expandir_tabulaciones("uno\t dos\tfin", 4) == "uno  dos    fin"
    assert core.contar_subcadena("banana", "na") == 2
    assert core.contar_subcadena("banana", "na", 0, 3) == 0
    assert core.centrar_texto("cobra", 9, "*") == "**cobra**"
    with pytest.raises(TypeError):
        core.centrar_texto("cobra", 10, "--")
    assert core.rellenar_ceros("7", 3) == "007"
    assert core.encontrar_texto("banana", "na") == 2
    assert core.encontrar_texto("banana", "na", 2) == 2
    assert core.encontrar_texto("banana", "xy") == -1
    assert core.encontrar_texto("banana", "xy", por_defecto=None) is None
    assert core.encontrar_texto("mañana", "ña", 0, 4) == 2
    assert core.encontrar_derecha_texto("banana", "na") == 4
    assert core.encontrar_derecha_texto("banana", "na", 0, 4) == 2
    assert core.encontrar_derecha_texto("banana", "zz", por_defecto="") == ""
    assert core.indice_texto("banana", "na") == 2
    assert core.indice_texto("banana", "na", 2) == 2
    with pytest.raises(ValueError):
        core.indice_texto("banana", "zz")
    assert core.indice_texto("banana", "zz", por_defecto=-1) == -1
    assert core.indice_derecha_texto("banana", "na") == 4
    with pytest.raises(ValueError):
        core.indice_derecha_texto("banana", "zz")
    assert core.indice_derecha_texto("banana", "zz", por_defecto="nada") == "nada"
    with pytest.raises(TypeError):
        core.encontrar_texto("texto", 123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        core.encontrar_texto("texto", "t", inicio="0")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        core.encontrar_texto("texto", "t", fin="5")  # type: ignore[arg-type]
    assert core.formatear_texto("{}-{}", "hola", "cobra") == "hola-cobra"
    with pytest.raises(TypeError):
        core.formatear_texto(123, "hola")  # type: ignore[arg-type]
    assert core.formatear_texto_mapa("Hola {nombre}", {"nombre": "Cobra"}) == "Hola Cobra"
    with pytest.raises(TypeError):
        core.formatear_texto_mapa("Hola {nombre}", ["Cobra"])  # type: ignore[arg-type]
    tabla = core.tabla_traduccion_texto("áé", "ae", "í")
    assert tabla[ord("á")] == "a"
    assert tabla[ord("é")] == "e"
    assert tabla[ord("í")] is None
    assert core.traducir_texto("áéí", tabla) == "ae"
    assert core.traducir_texto("sin cambios", {}) == "sin cambios"
    with pytest.raises(TypeError):
        core.tabla_traduccion_texto(123)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        core.tabla_traduccion_texto("ab", "c")
    with pytest.raises(TypeError):
        core.traducir_texto("texto", [1, 2, 3])  # type: ignore[arg-type]
    assert core.rellenar_ceros("-5", 4) == "-005"
    assert core.rellenar_ceros("猫", 3) == "00猫"
    assert core.minusculas_casefold("Straße") == "strasse"
    assert core.rellenar_izquierda("7", 3, "0") == "007"
    assert core.rellenar_derecha("7", 3, "0") == "700"
    with pytest.raises(ValueError):
        core.rellenar_izquierda("hola", 10, "")
    assert core.normalizar_unicode("A\u0301", "NFC") == "Á"
    with pytest.raises(ValueError):
        core.normalizar_unicode("hola", "XYZ")
    assert core.particionar_texto("mañana", "ñ") == ("ma", "ñ", "ana")
    assert core.particionar_texto("毒🐍", "🐍") == ("毒", "🐍", "")
    assert core.particionar_texto("sin", "x") == ("sin", "", "")
    with pytest.raises(TypeError):
        core.particionar_texto("abc", 123)
    with pytest.raises(ValueError):
        core.particionar_texto("abc", "")
    assert core.particionar_derecha("uno-dos-tres", "-") == ("uno-dos", "-", "tres")
    assert core.particionar_derecha("sin", "-") == ("", "", "sin")
    assert core.particionar_derecha("mañana", "a") == ("mañan", "a", "")
    assert core.codificar_texto("Señal", "latin-1") == b"Se\xf1al"
    with pytest.raises(UnicodeEncodeError):
        core.codificar_texto("€", "ascii")
    assert core.codificar_texto("hola€", "ascii", errores="ignore") == b"hola"
    assert core.decodificar_texto(b"Se\xf1al", "latin-1") == "Señal"
    with pytest.raises(UnicodeDecodeError):
        core.decodificar_texto(b"\xff", "utf-8")
    assert core.decodificar_texto(b"hola\xff", "utf-8", errores="ignore") == "hola"
    with pytest.raises(TypeError):
        core.codificar_texto(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        core.decodificar_texto("texto")  # type: ignore[arg-type]


def test_numero_funcs():
    assert core.es_finito(42) is True
    assert core.es_finito(0.0) is True
    assert core.es_finito(float("inf")) is False
    assert core.es_finito(float("nan")) is False
    assert core.es_infinito(float("inf")) is True
    assert core.es_infinito(float("-inf")) is True
    assert core.es_infinito(3.14) is False
    assert core.es_nan(float("nan")) is True
    assert core.es_nan(1.0) is False
    with pytest.raises(TypeError):
        core.es_finito("0")
    with pytest.raises(TypeError):
        core.es_infinito(b"1")
    with pytest.raises(TypeError):
        core.es_nan(object())
    assert core.copiar_signo(3.0, -2.0) == pytest.approx(-3.0)
    assert core.copiar_signo(-2.5, 7.0) == pytest.approx(2.5)
    cero_negativo = core.copiar_signo(0.0, -0.0)
    assert math.copysign(1.0, cero_negativo) == -1.0
    nan_resultado = core.copiar_signo(float("nan"), -1.0)
    assert math.isnan(nan_resultado)
    with pytest.raises(TypeError):
        core.copiar_signo("1", 1)

    assert core.signo(-5) == -1
    assert core.signo(0) == 0
    assert core.signo(2.5) == pytest.approx(1.0)
    assert math.copysign(1.0, core.signo(-0.0)) == -1.0
    assert math.isnan(core.signo(float("nan")))
    with pytest.raises(TypeError):
        core.signo("1")

    assert core.limitar(5, 0, 10) == 5
    assert core.limitar(-5, -3, 3) == -3
    assert core.limitar(2.5, 0.0, 1.0) == pytest.approx(1.0)
    assert math.isnan(core.limitar(float("nan"), 0.0, 1.0))
    assert math.isnan(core.limitar(1.0, float("nan"), 2.0))
    with pytest.raises(ValueError):
        core.limitar(0, 2, 1)
    with pytest.raises(TypeError):
        core.limitar(0, 1, "2")

    assert core.absoluto(-5) == 5
    assert core.absoluto(-5.2) == pytest.approx(5.2)
    assert core.redondear(3.14159, 2) == pytest.approx(3.14)
    assert core.redondear(3.6) == 4
    assert core.piso(3.9) == 3
    assert core.techo(3.1) == 4
    assert core.mcd(48, 18) == 6
    assert core.mcm(4, 6, 8) == 24
    assert core.es_cercano(1.0, 1.0 + 1e-10) is True
    assert core.es_cercano(1.0, 1.1, tolerancia_relativa=0.2) is True
    assert core.raiz(9) == pytest.approx(3.0)
    assert core.raiz(-8, 3) == pytest.approx(-2.0)
    assert core.potencia(2, 3) == pytest.approx(8.0)
    assert core.clamp(5, 0, 3) == 3
    assert core.interpolar(0.0, 10.0, 0.25) == pytest.approx(2.5)
    assert core.interpolar(-5, 5, -1.0) == pytest.approx(-5.0)
    assert core.interpolar(-5, 5, 2.0) == pytest.approx(5.0)
    assert core.envolver_modular(7, 5) == 2
    assert core.envolver_modular(-2, 5) == 3


    assert core.envolver_modular(7.5, -5.0) == pytest.approx(-2.5)
    with pytest.raises(ZeroDivisionError):
        core.envolver_modular(1, 0)
    assert 1 <= core.aleatorio(1, 2, semilla=42) <= 2
    assert core.mediana([1, 2, 3, 4]) == 2.5
    assert core.moda([1, 1, 2, 2, 2]) == 2
    assert core.producto([2, 3, 5]) == 30
    assert core.producto([], inicio=10) == 10
    assert core.longitud_bits(0) == 0
    assert core.longitud_bits(15) == 4
    assert core.longitud_bits(-10) == 4
    assert core.contar_bits(0) == 0
    assert core.contar_bits(255) == 8
    assert core.contar_bits(-3) == 2
    assert core.rotar_bits_izquierda(0b1011, 1) == 0b0111
    assert core.rotar_bits_izquierda(0b1011, 5) == 0b0111
    assert core.rotar_bits_derecha(0b1011, 1) == 0b1101
    assert core.rotar_bits_derecha(0b1011, 5) == 0b1101
    assert core.rotar_bits_izquierda(-2, 1, ancho_bits=8) == -3
    assert core.rotar_bits_derecha(-2, 2, ancho_bits=8) == -65
    assert core.rotar_bits_izquierda(0x1234, 20, ancho_bits=16) == 0x2341
    assert core.rotar_bits_derecha(0x1234, 20, ancho_bits=16) == 0x4123
    assert core.rotar_bits_izquierda(0x80000001, 36, ancho_bits=32) == 0x18
    assert core.rotar_bits_derecha(0x80000001, 36, ancho_bits=32) == 0x18000000
    with pytest.raises(ValueError):
        core.rotar_bits_izquierda(1, 1, ancho_bits=0)
    assert core.entero_a_base(255, 16) == "FF"
    assert core.entero_a_base(-10, 2) == "-1010"
    assert core.entero_desde_base("ff", 16) == 255
    assert core.entero_desde_base("-1010", 2) == -10
    assert core.entero_a_bytes(0, byteorder="big") == b"\x00"
    assert core.entero_a_bytes(255, byteorder="big") == b"\xff"
    assert core.entero_a_bytes(255, 2, byteorder="little") == b"\xff\x00"
    assert core.entero_a_bytes(-1, byteorder="big", signed=True) == b"\xff"
    assert core.entero_a_bytes(-129, byteorder="big", signed=True) == b"\xff\x7f"
    with pytest.raises(OverflowError):
        core.entero_a_bytes(256, 1, byteorder="big")
    with pytest.raises(OverflowError):
        core.entero_a_bytes(-5, byteorder="big")
    with pytest.raises(ValueError):
        core.entero_a_bytes(1, 1, byteorder="medio")
    assert core.entero_desde_bytes(b"\xff", byteorder="big") == 255
    assert core.entero_desde_bytes(b"\xff", byteorder="big", signed=True) == -1
    assert core.entero_desde_bytes(bytearray(b"\xff\x00"), byteorder="little") == 255
    with pytest.raises(ValueError):
        core.entero_desde_bytes(b"\x00", byteorder="medio")
    datos = [2, 4, 4, 4, 5, 5, 7, 9]
    assert core.desviacion_estandar(datos) == pytest.approx(2.0)
    assert core.desviacion_estandar(datos, muestral=True) == pytest.approx(
        2.1380899353
    )
    assert core.varianza(datos) == pytest.approx(stats.pvariance(datos))
    assert core.varianza_muestral(datos) == pytest.approx(stats.variance(datos))

    geometrica = [1, 3, 9, 27]
    assert core.media_geometrica(geometrica) == pytest.approx(
        stats.geometric_mean(geometrica)
    )
    armonica = [1.5, 2.5, 4.0]
    assert core.media_armonica(armonica) == pytest.approx(
        stats.harmonic_mean(armonica)
    )
    assert core.media_armonica([1.0, 0.0, 3.0]) == pytest.approx(
        stats.harmonic_mean([1.0, 0.0, 3.0])
    )

    assert core.percentil(datos, 25) == pytest.approx(
        float(np.percentile(datos, 25, method="linear"))
    )
    q1, q2, q3 = core.cuartiles(datos)
    assert q1 == pytest.approx(float(np.percentile(datos, 25, method="linear")))
    assert q2 == pytest.approx(float(np.percentile(datos, 50, method="linear")))
    assert q3 == pytest.approx(float(np.percentile(datos, 75, method="linear")))
    assert core.rango_intercuartil(datos) == pytest.approx(q3 - q1)

    coef_poblacional = stats.pstdev(datos) / abs(stats.fmean(datos))
    coef_muestral = stats.stdev(datos) / abs(stats.fmean(datos))
    assert core.coeficiente_variacion(datos) == pytest.approx(coef_poblacional)
    assert core.coeficiente_variacion(datos, muestral=True) == pytest.approx(
        coef_muestral
    )
    assert core.es_par(4) is True
    assert core.es_par(5) is False
    assert core.es_primo(7) is True
    assert core.es_primo(4) is False
    assert core.factorial(5) == 120
    assert core.promedio([1, 2, 3]) == 2.0


@pytest.mark.asyncio
async def test_reintentar_async_reintenta_hasta_exito(monkeypatch):
    llamadas = 0
    esperas: list[float] = []

    async def falso_sleep(segundos: float):
        esperas.append(segundos)

    monkeypatch.setattr(asyncio, "sleep", falso_sleep)

    async def operacion():
        nonlocal llamadas
        llamadas += 1
        if llamadas < 3:
            raise ValueError("fallo transitorio")
        return "ok"

    resultado = await core.reintentar_async(
        operacion,
        intentos=4,
        excepciones=(ValueError,),
        retardo_inicial=0.5,
        factor_backoff=3.0,
        max_retardo=2.0,
        jitter=False,
    )

    assert resultado == "ok"
    assert llamadas == 3
    assert esperas == [0.5, 1.5]


@pytest.mark.asyncio
async def test_reintentar_async_aplica_jitter_determinista(monkeypatch):
    esperas: list[float] = []

    async def falso_sleep(segundos: float):
        esperas.append(segundos)

    monkeypatch.setattr(asyncio, "sleep", falso_sleep)

    llamadas = 0

    async def operacion():
        nonlocal llamadas
        llamadas += 1
        if llamadas == 1:
            raise RuntimeError("fallo")
        return "listo"

    def ajustar(base: float) -> float:
        return base / 2

    resultado = await core.reintentar_async(
        operacion,
        intentos=2,
        excepciones=(RuntimeError,),
        retardo_inicial=0.4,
        jitter=ajustar,
    )

    assert resultado == "listo"
    assert esperas == [0.2]


def test_logica_funcs():
    casos = [
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    ]
    for a, b in casos:
        assert core.conjuncion(a, b) is (a and b)
        assert core.disyuncion(a, b) is (a or b)
        assert core.negacion(a) is (not a)
        assert core.xor(a, b) is ((a and not b) or (not a and b))
        assert core.nand(a, b) is (not (a and b))
        assert core.nor(a, b) is (not (a or b))
        assert core.implica(a, b) is ((not a) or b)
        assert core.equivale(a, b) is (a is b)

    assert core.xor_multiple(True, False, True) is False
    assert core.xor_multiple(False, False, False) is False


def test_logica_entonces_si_no_valores_directos():
    assert core.entonces(True, "cobra") == "cobra"
    assert core.entonces(False, "cobra") is None
    assert core.si_no(False, 42) == 42
    assert core.si_no(True, 42) is None


def test_logica_entonces_si_no_perezoso():
    accion = MagicMock(return_value="ejecutado")
    assert core.entonces(True, accion) == "ejecutado"
    accion.assert_called_once_with()

    accion.reset_mock()
    accion.return_value = True
    assert core.entonces(False, accion) is None
    accion.assert_not_called()

    accion.reset_mock()
    accion.return_value = "omitido"
    assert core.si_no(False, accion) == "omitido"
    accion.assert_called_once_with()

    accion.reset_mock()
    accion.return_value = None
    assert core.si_no(True, accion) is None
    accion.assert_not_called()
    assert core.es_verdadero(True) is True
    assert core.es_verdadero(False) is False
    assert core.es_falso(True) is False
    assert core.es_falso(False) is True
    for valor in (1, "False", None):
        with pytest.raises(TypeError):
            core.es_verdadero(valor)
        with pytest.raises(TypeError):
            core.es_falso(valor)
    assert core.xor_multiple(True, True, True, False) is True

    assert core.todas([True, True, True]) is True
    assert core.todas([True, False, True]) is False
    assert core.alguna([False, False, True]) is True
    assert core.alguna([False, False, False]) is False

    casos_coleccion = [
        ([False, False], True, False, 0, True),
        ([True, False], False, True, 1, False),
        ([True, True, False], False, False, 2, True),
        ([True, True, True], False, False, 3, False),
    ]
    for valores, ninguna_esperado, solo_uno_esperado, conteo_esperado, paridad_esperada in casos_coleccion:
        assert core.ninguna(valores) is ninguna_esperado
        assert core.solo_uno(*valores) is solo_uno_esperado
        assert core.conteo_verdaderos(valores) == conteo_esperado
        assert core.paridad(valores) is paridad_esperada

    assert core.solo_uno(True, False, False, False) is True
    assert core.solo_uno(False, False, False) is False

    with pytest.raises(TypeError):
        core.conjuncion(1, True)
    with pytest.raises(TypeError):
        core.disyuncion(True, "no bool")
    with pytest.raises(TypeError):
        core.negacion("no bool")
    with pytest.raises(ValueError):
        core.xor_multiple(True)
    with pytest.raises(TypeError):
        core.xor_multiple(True, 0)
    with pytest.raises(TypeError):
        core.todas([True, 1])
    with pytest.raises(TypeError):
        core.alguna([False, None])
    with pytest.raises(ValueError):
        core.solo_uno()
    with pytest.raises(TypeError):
        core.solo_uno(True, 0)
    with pytest.raises(TypeError):
        core.ninguna([True, 1])
    with pytest.raises(TypeError):
        core.conteo_verdaderos([False, None])
    with pytest.raises(TypeError):
        core.paridad([True, "no bool"])


def test_logica_condicional_evalua_en_orden():
    eventos: list[str] = []

    def condicion(nombre: str, resultado: bool):
        def _callable() -> bool:
            eventos.append(nombre)
            return resultado

        return _callable

    def resultado(nombre: str, valor: str):
        def _callable() -> str:
            eventos.append(nombre)
            return valor

        return _callable

    valor = core.condicional(
        (condicion("c1", False), resultado("r1", "primero")),
        (condicion("c2", True), resultado("r2", "segundo")),
        (condicion("c3", True), resultado("r3", "tercero")),
    )

    assert valor == "segundo"
    assert eventos == ["c1", "c2", "r2"]


def test_logica_condicional_por_defecto_perezoso():
    condicion = MagicMock(return_value=False)
    resultado = MagicMock(return_value="no usado")
    por_defecto = MagicMock(return_value="defecto")

    obtenido = core.condicional((condicion, resultado), por_defecto=por_defecto)

    assert obtenido == "defecto"
    condicion.assert_called_once_with()
    resultado.assert_not_called()
    por_defecto.assert_called_once_with()


def test_logica_condicional_valida_entradas():
    with pytest.raises(ValueError):
        core.condicional((True,), (False, lambda: None))

    with pytest.raises(TypeError):
        core.condicional((lambda: 1, lambda: "valor"))


def test_logica_mayoria_exactamente_n_y_diferencia():
    assert core.mayoria([True, True, False]) is True
    assert core.mayoria([True, False, False]) is False

    with pytest.raises(ValueError):
        core.mayoria([])
    with pytest.raises(TypeError):
        core.mayoria([True, 1])

    assert core.exactamente_n([True, False, True, False], 2) is True
    assert core.exactamente_n([True, False], 0) is False
    assert core.exactamente_n([], 0) is True

    with pytest.raises(TypeError):
        core.exactamente_n([True], 1.5)
    with pytest.raises(TypeError):
        core.exactamente_n([True], True)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        core.exactamente_n([False], -1)

    assert core.diferencia_simetrica([True, False], [False, False]) == (True, False)
    assert core.diferencia_simetrica([True, False, True]) == (True, False, True)
    assert core.diferencia_simetrica(
        [True, False, True],
        [False, False, True],
        [True, True, False],
    ) == (False, True, False)

    with pytest.raises(ValueError):
        core.diferencia_simetrica()
    with pytest.raises(ValueError):
        core.diferencia_simetrica([True], [True, False])


def test_logica_tabla_verdad():
    tabla = core.tabla_verdad(
        lambda a, b: core.conjuncion(a, core.disyuncion(a, b)),
        nombres=("a", "b"),
        nombre_resultado="salida",
    )

    assert tabla == [
        {"a": False, "b": False, "salida": False},
        {"a": False, "b": True, "salida": False},
        {"a": True, "b": False, "salida": True},
        {"a": True, "b": True, "salida": True},
    ]

    tabla_inferida = core.tabla_verdad(lambda a: core.negacion(a))
    assert tabla_inferida == [
        {"p1": False, "resultado": True},
        {"p1": True, "resultado": False},
    ]

    with pytest.raises(TypeError):
        core.tabla_verdad(123)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        core.tabla_verdad(lambda a: a, nombres=("a", "b"))
    with pytest.raises(ValueError):
        core.tabla_verdad(lambda *valores: True)


def test_archivo_funcs(tmp_path, monkeypatch):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    nombre = "f.txt"
    core.escribir(nombre, "data")
    ruta = tmp_path / nombre
    assert core.existe(ruta)
    assert core.leer(nombre) == "data"
    core.eliminar(ruta)
    assert not core.existe(ruta)


@pytest.mark.parametrize(
    "func",
    [core.leer, lambda ruta: core.escribir(ruta, "dato")],
)
@pytest.mark.parametrize(
    "ruta",
    [
        lambda base: str((base / "absoluta.txt").resolve()),
        lambda _base: "../escape.txt",
    ],
)
def test_archivo_rechaza_rutas_invalidas(monkeypatch, tmp_path, func, ruta):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    with pytest.raises(ValueError):
        func(ruta(tmp_path))


def test_archivo_existe_rechaza_fuera_del_sandbox(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    archivo_forzado = tmp_path.parent / "fuera.txt"
    archivo_forzado.write_text("contenido", encoding="utf-8")

    assert not core.existe(str(archivo_forzado))
    assert not core.existe("../fuera.txt")


def test_archivo_eliminar_inexistente_no_falla(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    core.eliminar("no-existe.txt")


@pytest.mark.skipif(
    not hasattr(os, "symlink"), reason="La plataforma no soporta enlaces simbólicos"
)
def test_archivo_eliminar_no_sigue_enlace_fuera(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    objetivo = tmp_path.parent / "externo.txt"
    objetivo.write_text("seguro", encoding="utf-8")
    enlace = tmp_path / "enlace.txt"
    enlace.symlink_to(objetivo)

    with pytest.raises(ValueError):
        core.eliminar(enlace.name)

    assert objetivo.exists()


def test_tiempo_funcs(monkeypatch):
    ahora = core.ahora()
    assert isinstance(ahora, datetime)
    fecha = datetime(2020, 1, 2, 3, 4, 5)
    assert core.formatear(fecha, "%Y") == "2020"
    called = {}

    def fake_sleep(seg):
        called["v"] = seg

    monkeypatch.setattr(core_tiempo.time, "sleep", fake_sleep)
    core.dormir(0.01)
    assert called["v"] == 0.01


def test_coleccion_funcs():
    datos = [3, 1, 2, 1]
    assert core.ordenar(datos) == [1, 1, 2, 3]
    assert core.maximo(datos) == 3
    assert core.minimo(datos) == 1
    assert core.sin_duplicados(datos) == [3, 1, 2]
    assert core.mapear(datos, lambda x: x + 1) == [4, 2, 3, 2]
    assert core.filtrar(datos, lambda x: x % 2 == 0) == [2]
    assert core.mapear_aplanado([1, 3], lambda x: range(x)) == [0, 0, 1, 2]
    assert core.reducir([1, 2, 3], operator.add) == 6
    assert core.reducir([1, 2, 3], operator.add, 10) == 16
    assert core.encontrar(datos, lambda x: x > 2) == 3
    assert core.encontrar(datos, lambda x: x > 10, predeterminado="ninguno") == "ninguno"
    assert core.aplanar([[1, 2], (3, 4)]) == [1, 2, 3, 4]
    
    class Caja:
        def __init__(self, valor):
            self.valor = valor

    cajas = [Caja(1), Caja(2)]
    resultado_cajas = core.mapear_aplanado(cajas, lambda caja: (caja,))
    assert [c.valor for c in cajas] == [1, 2]
    assert all(isinstance(elem, Caja) for elem in resultado_cajas)
    assert resultado_cajas[0] is cajas[0]
    assert resultado_cajas[1] is cajas[1]

    estructuras = [
        {"tipo": "a", "valor": 1},
        {"tipo": "b", "valor": 2},
        {"tipo": "a", "valor": 3},
    ]
    agrupado = core.agrupar_por(estructuras, lambda x: x["tipo"])
    assert isinstance(agrupado, OrderedDict)
    assert list(agrupado.keys()) == ["a", "b"]
    assert [e["valor"] for e in agrupado["a"]] == [1, 3]

    class Objeto:
        def __init__(self, categoria):
            self.categoria = categoria

    objetos = [Objeto("x"), Objeto("x"), Objeto("y")]
    agrupados_objetos = core.agrupar_por(objetos, "categoria")
    assert list(agrupados_objetos.keys()) == ["x", "y"]

    pares, impares = core.particionar(range(5), lambda x: x % 2 == 0)
    assert pares == [0, 2, 4]
    assert impares == [1, 3]
    esperado = [1, 2, 3]
    random.Random(7).shuffle(esperado)
    assert core.mezclar([1, 2, 3], semilla=7) == esperado
    assert core.zip_listas([1, 2], ["a", "b", "c"]) == [(1, "a"), (2, "b")]
    assert core.zip_listas() == []
    assert core.tomar(datos, 2) == [3, 1]
    assert core.tomar(datos, 0) == []
    assert core.tomar_mientras([5, 4, 3, 0, 1], lambda x: x > 0) == [5, 4, 3]
    assert core.tomar_mientras([], lambda _: True) == []
    assert core.descartar_mientras([0, 0, 1, 2], lambda x: x == 0) == [1, 2]
    assert core.descartar_mientras([], lambda _: False) == []
    assert core.scanear([1, 2, 3], operator.add) == [1, 3, 6]
    assert core.scanear([1, 2, 3], operator.mul, 1) == [1, 1, 2, 6]
    assert core.scanear([], operator.add) == []
    assert core.scanear([], operator.add, 5) == [5]
    assert core.pares_consecutivos([1, 2, 3]) == [(1, 2), (2, 3)]
    assert core.pares_consecutivos([]) == []
    assert core.pares_consecutivos([1]) == []
    assert core.mapear([], lambda x: x) == []


def test_coleccion_validaciones():
    with pytest.raises(ValueError):
        core.maximo([])
    with pytest.raises(ValueError):
        core.minimo([])
    with pytest.raises(TypeError):
        core.mapear([1], None)
    with pytest.raises(TypeError):
        core.filtrar([1], "no callable")
    with pytest.raises(TypeError):
        core.mapear_aplanado([1], lambda _: 42)
    with pytest.raises(ValueError):
        core.reducir([], operator.add)
    with pytest.raises(TypeError):
        core.particionar([1], None)
    with pytest.raises(KeyError):
        core.agrupar_por([{"tipo": "a"}], "categoria")
    with pytest.raises(ValueError):
        core.tomar([1], -1)
    with pytest.raises(TypeError):
        core.tomar([1], 1.5)
    with pytest.raises(TypeError):
        core.tomar_mientras(123, lambda x: x)
    with pytest.raises(TypeError):
        core.tomar_mientras([1], None)
    with pytest.raises(TypeError):
        core.descartar_mientras(123, lambda x: x)
    with pytest.raises(TypeError):
        core.descartar_mientras([1], "no callable")
    with pytest.raises(TypeError):
        core.scanear([1, 2], "no callable")


def test_coleccion_excepciones():
    def explota(valor):
        raise RuntimeError("boom")

    def explota_scan(acumulado, valor):  # pragma: no cover - auxilia en prueba
        raise RuntimeError("scan")

    with pytest.raises(RuntimeError):
        core.tomar_mientras([1, 2, 3], explota)

    with pytest.raises(RuntimeError):
        core.descartar_mientras([0, 1, 2], explota)

    with pytest.raises(RuntimeError):
        core.scanear([1, 2, 3], explota_scan)


def test_seguridad_funcs():
    assert (
        core.hash_sha256("a")
        == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb"
    )
    uuid = core.generar_uuid()
    assert isinstance(uuid, str) and len(uuid) == 36


def test_red_funcs(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "x")
    mock_resp_get = MagicMock(url="https://x", encoding="utf-8")
    mock_resp_get.iter_content.return_value = [b"ok"]
    mock_resp_get.raise_for_status.return_value = None
    mock_resp_post = MagicMock(url="https://x", encoding="utf-8")
    mock_resp_post.iter_content.return_value = [b"ok"]
    mock_resp_post.raise_for_status.return_value = None
    with patch(
        "pcobra.corelibs.red.requests.get", return_value=mock_resp_get
    ) as mock_get, patch(
        "pcobra.corelibs.red.requests.post", return_value=mock_resp_post
    ) as mock_post:
        assert core.obtener_url("https://x") == "ok"
        assert core.enviar_post("https://x", {"a": 1}) == "ok"
        mock_get.assert_called_once_with(
            "https://x", timeout=5, allow_redirects=False, stream=True
        )
        mock_post.assert_called_once_with(
            "https://x", data={"a": 1}, timeout=5, allow_redirects=False, stream=True
        )


def test_red_obtener_url_rechaza_esquema_no_http(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("pcobra.corelibs.red.requests.get") as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("ftp://ejemplo.com")
        mock_get.assert_not_called()


def test_red_obtener_url_rechaza_otro_esquema(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("pcobra.corelibs.red.requests.get") as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("file:///tmp/archivo.txt")
        mock_get.assert_not_called()


def test_red_enviar_post_rechaza_esquema_no_http(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("pcobra.corelibs.red.requests.post") as mock_post:
        with pytest.raises(ValueError):
            core.enviar_post("ftp://ejemplo.com", {"a": 1})
        mock_post.assert_not_called()


def test_red_enviar_post_rechaza_otro_esquema(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("pcobra.corelibs.red.requests.post") as mock_post:
        with pytest.raises(ValueError):
            core.enviar_post("file:///tmp/archivo.txt", {"a": 1})
        mock_post.assert_not_called()


def test_red_host_whitelist_permite(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(url="https://example.com", encoding="utf-8")
    mock_resp.iter_content.return_value = [b"ok"]
    mock_resp.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.get", return_value=mock_resp) as mock_get:
        assert core.obtener_url("https://example.com") == "ok"
        mock_get.assert_called_once_with(
            "https://example.com", timeout=5, allow_redirects=False, stream=True
        )


def test_red_host_whitelist_rechaza(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("pcobra.corelibs.red.requests.get") as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("https://otro.com")
        mock_get.assert_not_called()


def test_red_obtener_url_redireccion_fuera_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(text="ok", url="https://otro.com")
    mock_resp.status_code = 302
    mock_resp.headers = {"location": "https://otro.com"}
    mock_resp.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.get", return_value=mock_resp):
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com", permitir_redirecciones=True)


def test_red_enviar_post_redireccion_fuera_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(text="ok", url="https://otro.com")
    mock_resp.status_code = 302
    mock_resp.headers = {"location": "https://otro.com"}
    mock_resp.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.post", return_value=mock_resp):
        with pytest.raises(ValueError):
            core.enviar_post(
                "https://example.com", {"a": 1}, permitir_redirecciones=True
            )


def test_red_obtener_url_respuesta_muy_grande(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    grande = MagicMock(url="https://example.com", encoding="utf-8")
    grande.iter_content.return_value = [b"a" * (1024 * 1024 + 1)]
    grande.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.get", return_value=grande):
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com")
    grande.close.assert_called_once()


def test_red_enviar_post_respuesta_muy_grande(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    grande = MagicMock(url="https://example.com", encoding="utf-8")
    grande.iter_content.return_value = [b"a" * (1024 * 1024 + 1)]
    grande.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.post", return_value=grande):
        with pytest.raises(ValueError):
            core.enviar_post("https://example.com", {"a": 1})
    grande.close.assert_called_once()


def test_sistema_funcs(tmp_path, monkeypatch):
    assert core.obtener_os() == os.uname().sysname
    proc = MagicMock()
    proc.stdout = "hola\n"

    def fake_run(*a, **k):
        assert k["timeout"] == 1
        return proc

    monkeypatch.setattr(core_sistema.subprocess, "run", fake_run)
    permitido = core_sistema.os.path.realpath("/usr/bin/echo")
    assert (
        core.ejecutar(["echo", "hola"], permitidos=[permitido], timeout=1)
        == "hola\n"
    )
    os.environ["PRUEBA"] = "1"
    assert core.obtener_env("PRUEBA") == "1"
    d = tmp_path
    (d / "x").write_text("")
    assert "x" in core.listar_dir(d)


def test_transpile_texto():
    ast = [
        NodoLlamadaFuncion("mayusculas", [NodoValor("'hola'")]),
        NodoLlamadaFuncion("minusculas", [NodoValor("'HOLA'")]),
        NodoLlamadaFuncion("capitalizar", [NodoValor("'cobra'")]),
        NodoLlamadaFuncion("titulo", [NodoValor("'cobra feroz'")]),
        NodoLlamadaFuncion("invertir", [NodoValor("'abc'")]),
        NodoLlamadaFuncion("concatenar", [NodoValor("'a'"), NodoValor("'b'")]),
        NodoLlamadaFuncion("quitar_espacios", [NodoValor("'  hola  '")]),
        NodoLlamadaFuncion("dividir", [NodoValor("'a b c'")]),
        NodoLlamadaFuncion("unir", [NodoValor("'-'"), NodoValor('["a","b"]')]),
        NodoLlamadaFuncion(
            "reemplazar",
            [
                NodoValor("'banana'"),
                NodoValor("'na'"),
                NodoValor("'NA'"),
                NodoValor(1),
            ],
        ),
        NodoLlamadaFuncion("empieza_con", [NodoValor("'cobra'"), NodoValor("'co'")]),
        NodoLlamadaFuncion("termina_con", [NodoValor("'cobra'"), NodoValor("'bra'")]),
        NodoLlamadaFuncion("incluye", [NodoValor("'cobra'"), NodoValor("'ob'")]),
        NodoLlamadaFuncion(
            "rellenar_izquierda",
            [NodoValor("'7'"), NodoValor(3), NodoValor("'0'")],
        ),
        NodoLlamadaFuncion(
            "rellenar_derecha",
            [NodoValor("'7'"), NodoValor(3), NodoValor("'0'")],
        ),
        NodoLlamadaFuncion(
            "normalizar_unicode", [NodoValor("'Á'"), NodoValor("'NFD'")]
        ),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "mayusculas('hola')\n"
        + "minusculas('HOLA')\n"
        + "capitalizar('cobra')\n"
        + "titulo('cobra feroz')\n"
        + "invertir('abc')\n"
        + "concatenar('a', 'b')\n"
        + "quitar_espacios('  hola  ')\n"
        + "dividir('a b c')\n"
        + "unir('-', [\"a\",\"b\"])\n"
        + "reemplazar('banana', 'na', 'NA', 1)\n"
        + "empieza_con('cobra', 'co')\n"
        + "termina_con('cobra', 'bra')\n"
        + "incluye('cobra', 'ob')\n"
        + "rellenar_izquierda('7', 3, '0')\n"
        + "rellenar_derecha('7', 3, '0')\n"
        + "normalizar_unicode('Á', 'NFD')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "mayusculas('hola');\n"
        + "minusculas('HOLA');\n"
        + "capitalizar('cobra');\n"
        + "titulo('cobra feroz');\n"
        + "invertir('abc');\n"
        + "concatenar('a', 'b');\n"
        + "quitar_espacios('  hola  ');\n"
        + "dividir('a b c');\n"
        + "unir('-', [\"a\",\"b\"]);\n"
        + "reemplazar('banana', 'na', 'NA', 1);\n"
        + "empieza_con('cobra', 'co');\n"
        + "termina_con('cobra', 'bra');\n"
        + "incluye('cobra', 'ob');\n"
        + "rellenar_izquierda('7', 3, '0');\n"
        + "rellenar_derecha('7', 3, '0');\n"
        + "normalizar_unicode('Á', 'NFD');"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_texto_busquedas():
    ast = [
        NodoLlamadaFuncion("encontrar_texto", [NodoValor("'banana'"), NodoValor("'na'")]),
        NodoLlamadaFuncion("indice_texto", [NodoValor("'banana'"), NodoValor("'na'")]),
        NodoLlamadaFuncion(
            "formatear_texto",
            [NodoValor("'{} {}'"), NodoValor("'hola'"), NodoValor("'cobra'")],
        ),
        NodoLlamadaFuncion(
            "formatear_texto_mapa",
            [NodoValor("'Hola {nombre}'"), NodoValor("{'nombre': 'Cobra'}")],
        ),
        NodoLlamadaFuncion(
            "traducir_texto",
            [
                NodoValor("'áéí'"),
                NodoValor("tabla_traduccion_texto('áé', 'ae', 'í')"),
            ],
        ),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "encontrar_texto('banana', 'na')\n"
        + "indice_texto('banana', 'na')\n"
        + "formatear_texto('{} {}', 'hola', 'cobra')\n"
        + "formatear_texto_mapa('Hola {nombre}', {'nombre': 'Cobra'})\n"
        + "traducir_texto('áéí', tabla_traduccion_texto('áé', 'ae', 'í'))\n"
    )
    js_exp = (
        IMPORTS_JS
        + "encontrar_texto(NodoValor(valor=\"'banana'\"), NodoValor(valor=\"'na'\"));\n"
        + "indice_texto(NodoValor(valor=\"'banana'\"), NodoValor(valor=\"'na'\"));\n"
        + "formatear_texto(NodoValor(valor=\"'{} {}'\"), NodoValor(valor=\"'hola'\"), NodoValor(valor=\"'cobra'\"));\n"
        + "formatear_texto_mapa(NodoValor(valor=\"'Hola {nombre}'\"), NodoValor(valor=\"{'nombre': 'Cobra'}\"));\n"
        + "traducir_texto(NodoValor(valor=\"'áéí'\"), NodoValor(valor=\"tabla_traduccion_texto('áé', 'ae', 'í')\"));"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_numero():
    ast = [
        NodoLlamadaFuncion("absoluto", [NodoValor(-5)]),
        NodoLlamadaFuncion("redondear", [NodoValor(3.14159), NodoValor(2)]),
        NodoLlamadaFuncion("piso", [NodoValor(3.9)]),
        NodoLlamadaFuncion("techo", [NodoValor(3.1)]),
        NodoLlamadaFuncion("raiz", [NodoValor(9)]),
        NodoLlamadaFuncion("potencia", [NodoValor(2), NodoValor(3)]),
        NodoLlamadaFuncion("clamp", [NodoValor(5), NodoValor(0), NodoValor(3)]),
        NodoLlamadaFuncion("aleatorio", [NodoValor(1), NodoValor(2)]),
        NodoLlamadaFuncion("mediana", [NodoValor("[1,2,3]")]),
        NodoLlamadaFuncion("moda", [NodoValor("[1,1,2]")]),
        NodoLlamadaFuncion("desviacion_estandar", [NodoValor("[1,2,3]")]),
        NodoLlamadaFuncion("es_par", [NodoValor(2)]),
        NodoLlamadaFuncion("es_primo", [NodoValor(3)]),
        NodoLlamadaFuncion("factorial", [NodoValor(3)]),
        NodoLlamadaFuncion("promedio", [NodoValor("[1,2]")]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "absoluto(-5)\n"
        + "redondear(3.14159, 2)\n"
        + "piso(3.9)\n"
        + "techo(3.1)\n"
        + "raiz(9)\n"
        + "potencia(2, 3)\n"
        + "clamp(5, 0, 3)\n"
        + "aleatorio(1, 2)\n"
        + "mediana([1,2,3])\n"
        + "moda([1,1,2])\n"
        + "desviacion_estandar([1,2,3])\n"
        + "es_par(2)\n"
        + "es_primo(3)\n"
        + "factorial(3)\n"
        + "promedio([1,2])\n"
    )
    js_exp = (
        IMPORTS_JS
        + "absoluto(-5);\n"
        + "redondear(3.14159, 2);\n"
        + "piso(3.9);\n"
        + "techo(3.1);\n"
        + "raiz(9);\n"
        + "potencia(2, 3);\n"
        + "clamp(5, 0, 3);\n"
        + "aleatorio(1, 2);\n"
        + "mediana([1,2,3]);\n"
        + "moda([1,1,2]);\n"
        + "desviacion_estandar([1,2,3]);\n"
        + "es_par(2);\n"
        + "es_primo(3);\n"
        + "factorial(3);\n"
        + "promedio([1,2]);"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_archivo():
    ast = [
        NodoLlamadaFuncion("leer", [NodoValor("'f.txt'")]),
        NodoLlamadaFuncion("escribir", [NodoValor("'f.txt'"), NodoValor("'x'")]),
        NodoLlamadaFuncion("existe", [NodoValor("'f.txt'")]),
        NodoLlamadaFuncion("eliminar", [NodoValor("'f.txt'")]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "leer('f.txt')\n"
        + "escribir('f.txt', 'x')\n"
        + "existe('f.txt')\n"
        + "eliminar('f.txt')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "leer('f.txt');\n"
        + "escribir('f.txt', 'x');\n"
        + "existe('f.txt');\n"
        + "eliminar('f.txt');"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_tiempo():
    ast = [
        NodoLlamadaFuncion("ahora", []),
        NodoLlamadaFuncion("formatear", [NodoValor("fecha"), NodoValor("'%Y'")]),
        NodoLlamadaFuncion("dormir", [NodoValor(1)]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = IMPORTS_PY + "ahora()\n" + "formatear(fecha, '%Y')\n" + "dormir(1)\n"
    js_exp = IMPORTS_JS + "ahora();\n" + "formatear(fecha, '%Y');\n" + "dormir(1);"
    assert py == py_exp
    assert js == js_exp


def test_transpile_coleccion():
    ast = [
        NodoLlamadaFuncion("ordenar", [NodoValor("[3,1]")]),
        NodoLlamadaFuncion("maximo", [NodoValor("[1,2]")]),
        NodoLlamadaFuncion("minimo", [NodoValor("[1,2]")]),
        NodoLlamadaFuncion("sin_duplicados", [NodoValor("[1,1]")]),
        NodoLlamadaFuncion("mapear", [NodoValor("[1,2]"), NodoValor("duplicar")]),
        NodoLlamadaFuncion("filtrar", [NodoValor("[1,2,3]"), NodoValor("es_par")]),
        NodoLlamadaFuncion(
            "reducir",
            [NodoValor("[1,2,3]"), NodoValor("sumar"), NodoValor(0)],
        ),
        NodoLlamadaFuncion("encontrar", [NodoValor("[1,2,3]"), NodoValor("es_par")]),
        NodoLlamadaFuncion("aplanar", [NodoValor("[[1,2],[3,4]]")]),
        NodoLlamadaFuncion("agrupar_por", [NodoValor("datos"), NodoValor("'tipo'")]),
        NodoLlamadaFuncion("particionar", [NodoValor("[1,2,3]"), NodoValor("es_par")]),
        NodoLlamadaFuncion("mezclar", [NodoValor("[1,2,3]"), NodoValor(1)]),
        NodoLlamadaFuncion("zip_listas", [NodoValor("[1,2]"), NodoValor("[3,4]")]),
        NodoLlamadaFuncion("tomar", [NodoValor("[1,2,3]"), NodoValor(2)]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "ordenar([3,1])\n"
        + "maximo([1,2])\n"
        + "minimo([1,2])\n"
        + "sin_duplicados([1,1])\n"
        + "mapear([1,2], duplicar)\n"
        + "filtrar([1,2,3], es_par)\n"
        + "reducir([1,2,3], sumar, 0)\n"
        + "encontrar([1,2,3], es_par)\n"
        + "aplanar([[1,2],[3,4]])\n"
        + "agrupar_por(datos, 'tipo')\n"
        + "particionar([1,2,3], es_par)\n"
        + "mezclar([1,2,3], 1)\n"
        + "zip_listas([1,2], [3,4])\n"
        + "tomar([1,2,3], 2)\n"
    )
    js_exp = (
        IMPORTS_JS
        + "ordenar([3,1]);\n"
        + "maximo([1,2]);\n"
        + "minimo([1,2]);\n"
        + "sin_duplicados([1,1]);\n"
        + "mapear([1,2], duplicar);\n"
        + "filtrar([1,2,3], es_par);\n"
        + "reducir([1,2,3], sumar, 0);\n"
        + "encontrar([1,2,3], es_par);\n"
        + "aplanar([[1,2],[3,4]]);\n"
        + "agrupar_por(datos, 'tipo');\n"
        + "particionar([1,2,3], es_par);\n"
        + "mezclar([1,2,3], 1);\n"
        + "zip_listas([1,2], [3,4]);\n"
        + "tomar([1,2,3], 2);"
    )
    assert py == py_exp
    assert js == js_exp


@pytest.mark.asyncio
async def test_grupo_tareas_propaga_errores():
    async def tarea_exitosa():
        await asyncio.sleep(0)
        return "ok"

    async def tarea_fallida():
        await asyncio.sleep(0)
        raise RuntimeError("fallo intencional")

    with pytest.raises(ExceptionGroup) as excinfo:
        async with core.grupo_tareas() as grupo:
            grupo.create_task(tarea_exitosa())
            grupo.create_task(tarea_fallida())

    assert any(isinstance(error, RuntimeError) for error in excinfo.value.exceptions)


@pytest.mark.asyncio
async def test_grupo_tareas_cancela_pendientes():
    cancelado = asyncio.Event()

    async def tarea_larga():
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cancelado.set()
            raise

    async def tarea_que_falla():
        raise ValueError("boom")

    with pytest.raises(ExceptionGroup):
        async with core.grupo_tareas() as grupo:
            grupo.create_task(tarea_larga())
            grupo.create_task(tarea_que_falla())

    assert cancelado.is_set()


def test_hipotenusa_y_distancia_euclidiana_core():
    assert core.hipotenusa(3, 4) == pytest.approx(5.0)
    assert core.hipotenusa([2, 3, 6]) == pytest.approx(math.sqrt(49.0))

    punto_a = (0.0, 0.0, 0.0)
    punto_b = (1.0, 2.0, 2.0)
    assert core.distancia_euclidiana(punto_a, punto_b) == pytest.approx(3.0)

    with pytest.raises(TypeError):
        core.hipotenusa()
    with pytest.raises(TypeError):
        core.hipotenusa("34")
    with pytest.raises(TypeError):
        core.distancia_euclidiana("00", "11")
    with pytest.raises(TypeError):
        core.distancia_euclidiana([1, "b"], [0, 0])
    with pytest.raises(ValueError):
        core.distancia_euclidiana([0.0, 0.0], [1.0])


def test_transpile_seguridad():
    ast = [
        NodoLlamadaFuncion("hash_sha256", [NodoValor("'a'")]),
        NodoLlamadaFuncion("generar_uuid", []),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = IMPORTS_PY + "hash_sha256('a')\n" + "generar_uuid()\n"
    js_exp = IMPORTS_JS + "hash_sha256('a');\n" + "generar_uuid();"
    assert py == py_exp
    assert js == js_exp


def test_transpile_red():
    ast = [
        NodoLlamadaFuncion("obtener_url", [NodoValor("'https://x'")]),
        NodoLlamadaFuncion(
            "enviar_post", [NodoValor("'https://x'"), NodoValor('{"a":1}')]
        ),
        NodoLlamadaFuncion("obtener_url_async", [NodoValor("'https://x'")]),
        NodoLlamadaFuncion(
            "enviar_post_async",
            [NodoValor("'https://x'"), NodoValor('{"a":1}')],
        ),
        NodoLlamadaFuncion(
            "descargar_archivo",
            [NodoValor("'https://x'"), NodoValor("'salida.bin'")],
        ),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "obtener_url('https://x')\n"
        + "enviar_post('https://x', {\"a\":1})\n"
        + "obtener_url_async('https://x')\n"
        + "enviar_post_async('https://x', {\"a\":1})\n"
        + "descargar_archivo('https://x', 'salida.bin')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "obtener_url('https://x');\n"
        + "enviar_post('https://x', {\"a\":1});\n"
        + "obtener_url_async('https://x');\n"
        + "enviar_post_async('https://x', {\"a\":1});\n"
        + "descargar_archivo('https://x', 'salida.bin');"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_sistema():
    ast = [
        NodoLlamadaFuncion("obtener_os", []),
        NodoLlamadaFuncion("ejecutar", [NodoValor("['ls']")]),
        NodoLlamadaFuncion("obtener_env", [NodoValor("'PATH'")]),
        NodoLlamadaFuncion("listar_dir", [NodoValor("'.'")]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "obtener_os()\n"
        + "ejecutar(['ls'])\n"
        + "obtener_env('PATH')\n"
        + "listar_dir('.')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "obtener_os();\n"
        + "ejecutar(['ls']);\n"
        + "obtener_env('PATH');\n"
        + "listar_dir('.');"
    )
    assert py == py_exp
    assert js == js_exp
