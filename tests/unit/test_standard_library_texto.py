import sys
from types import ModuleType

import pytest

try:  # pragma: no cover - entorno de CI sin dependencias opcionales
    import numpy  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover - fallback para ejecutar pruebas sin numpy
    modulo_numpy = ModuleType("numpy")
    modulo_numpy.isscalar = lambda obj: False
    modulo_numpy.ndarray = type("ndarray", (), {})
    sys.modules["numpy"] = modulo_numpy

try:  # pragma: no cover - entorno de CI sin dependencias opcionales
    import pandas  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover - fallback para ejecutar pruebas sin pandas
    sys.modules.setdefault("pandas", ModuleType("pandas"))

import standard_library.texto as texto


def test_quitar_acentos():
    assert texto.quitar_acentos("Canción") == "Cancion"
    assert texto.quitar_acentos("pingüino") == "pinguino"


def test_normalizar_espacios():
    assert texto.normalizar_espacios("  hola\t mundo \n") == "hola mundo"
    assert texto.normalizar_espacios("") == ""


def test_es_palindromo_variantes():
    assert texto.es_palindromo("Sé verlas al revés") is True
    assert texto.es_palindromo("áa") is True
    assert texto.es_palindromo("áa", ignorar_tildes=False) is False
    assert texto.es_palindromo("Roma", ignorar_espacios=False) is False


def test_es_anagrama():
    assert texto.es_anagrama("Roma", "amor") is True
    assert texto.es_anagrama("cosa", "caso") is True
    assert texto.es_anagrama("cosa", "caso ", ignorar_espacios=False) is False


def test_a_snake_y_a_camel():
    assert texto.a_snake("HolaMundo") == "hola_mundo"
    assert texto.a_snake("mañana-tarde Noche") == "mañana_tarde_noche"
    assert texto.a_snake("JSONDataLoader") == "json_data_loader"
    assert texto.a_camel("hola mundo") == "holaMundo"
    assert texto.a_camel("mañana_tarde noche", inicial_mayuscula=True) == "MañanaTardeNoche"
    assert texto.a_camel("datos-JSON_parser") == "datosJsonParser"


def test_quitar_envoltura_normaliza():
    assert texto.quitar_envoltura("«mañana»", "«", "»") == "mañana"
    assert texto.quitar_envoltura("cancio\u0301n", "can", "ón") == "ci"
    assert texto.quitar_envoltura("⚡dato⚡", "", "⚡") == "⚡dato"


def test_prefijos_y_sufijos():
    assert texto.quitar_prefijo("🧪Prueba", "🧪") == "Prueba"
    assert texto.quitar_prefijo("demo", "x") == "demo"
    assert texto.quitar_sufijo("archivo.log", ".log") == "archivo"
    assert texto.quitar_sufijo("archivo.log", ".gz") == "archivo.log"


def test_prefijo_y_sufijo_comun():
    assert texto.prefijo_comun("mañana", "Mañanita", ignorar_mayusculas=True) == "mañan"
    assert texto.prefijo_comun(
        "Canción",
        "cancio\u0301n",
        ignorar_mayusculas=True,
        normalizar="NFC",
    ) == "Canción"
    assert texto.prefijo_comun("東京タワー", "東京ドーム") == "東京"
    assert texto.sufijo_comun("astronomía", "economía") == "onomía"
    assert texto.sufijo_comun(
        "Αθηναϊκό",
        "Λαϊκό",
        ignorar_mayusculas=True,
        normalizar="NFC",
    ) == "αϊκό"
    assert texto.sufijo_comun("hola", "mundo") == ""


def test_dividir_lineas_y_contar():
    contenido = "uno\r\ndos\n"
    assert texto.dividir_lineas(contenido) == ["uno", "dos"]
    assert texto.dividir_lineas(contenido, conservar_delimitadores=True) == [
        "uno\r\n",
        "dos\n",
    ]
    assert texto.contar_subcadena("bananana", "na") == 3
    assert texto.contar_subcadena("bananana", "na", 2) == 3
    assert texto.contar_subcadena("bananana", "na", 0, 5) == 1


def test_indentar_y_desindentar():
    bloque = "uno\n  dos\n\n"
    assert texto.indentar_texto(bloque, "-> ") == "-> uno\n->   dos\n-> \n"
    assert texto.indentar_texto(bloque, "-> ", solo_lineas_no_vacias=True) == "-> uno\n->   dos\n\n"
    sangrado = "    uno\n        dos\n    tres"
    assert texto.desindentar_texto(sangrado) == "uno\n    dos\ntres"


def test_envolver_y_acortar_texto():
    parrafo = "Cobra facilita scripts portables y claros."
    esperado = [
        "* Cobra facilita",
        "  scripts",
        "  portables y",
        "  claros.",
    ]
    assert texto.envolver_texto(
        parrafo,
        18,
        indentacion_inicial="* ",
        indentacion_subsecuente="  ",
    ) == esperado
    como_parrafo = texto.envolver_texto(
        parrafo,
        18,
        indentacion_inicial="* ",
        indentacion_subsecuente="  ",
        como_texto=True,
    )
    assert como_parrafo == "\n".join(esperado)
    assert texto.acortar_texto("Cobra facilita herramientas", 32) == "Cobra facilita herramientas"
    assert texto.acortar_texto("Cobra facilita herramientas", 18) == "Cobra [...]"


def test_centrar_rellenar_y_casefold():
    assert texto.centrar_texto("cobra", 9, "*") == "**cobra**"
    with pytest.raises(TypeError):
        texto.centrar_texto("cobra", 10, "--")
    assert texto.rellenar_ceros("-5", 4) == "-005"
    assert texto.rellenar_ceros("猫", 3) == "00猫"
    assert texto.minusculas_casefold("Straße") == "strasse"


def test_intercambiar_y_expandir():
    assert texto.intercambiar_mayusculas("ÁRBOL y Cobra") == "árbol Y cOBRA"
    assert texto.expandir_tabulaciones("uno\t dos\tfin", tabulaciones=4) == "uno  dos    fin"


def test_subcadenas():
    assert texto.subcadena_antes("uno-dos", "-") == "uno"
    assert texto.subcadena_despues("uno-dos", "-") == "dos"
    assert texto.subcadena_antes_ultima("uno-dos-tres", "-") == "uno-dos"
    assert texto.subcadena_despues_ultima("uno-dos-tres", "-") == "tres"
    assert texto.subcadena_antes("texto", "|") == "texto"
    assert texto.subcadena_despues("texto", "|") == "texto"
    assert texto.subcadena_antes("texto", "|", "N/A") == "N/A"
    assert texto.subcadena_despues("texto", "|", "N/A") == "N/A"
    assert texto.subcadena_antes_ultima("texto", "|", "N/A") == "N/A"
    assert texto.subcadena_despues_ultima("texto", "|", "N/A") == "N/A"
    cadena = "毒🐍🍎"
    assert texto.subcadena_antes(cadena, "🐍") == "毒"
    assert texto.subcadena_despues(cadena, "🐍") == "🍎"
    assert texto.subcadena_antes_ultima(cadena, "🐍") == "毒"
    assert texto.subcadena_despues_ultima(cadena, "🐍") == "🍎"
    assert texto.subcadena_antes("abc", "") == ""
    assert texto.subcadena_despues("abc", "") == "abc"
    assert texto.subcadena_antes_ultima("abc", "") == "abc"
    assert texto.subcadena_despues_ultima("abc", "") == ""


def test_dividir_y_particionar():
    assert texto.dividir_derecha("uno-dos-tres", "-", 1) == ["uno-dos", "tres"]
    assert texto.dividir_derecha("  α  β  γ  ", None, 1) == ["  α  β", "γ"]
    with pytest.raises(ValueError):
        texto.dividir_derecha("abc", "")
    assert texto.particionar("mañana", "ñ") == ("ma", "ñ", "ana")
    assert texto.particionar("毒🐍", "🐍") == ("毒", "🐍", "")
    assert texto.particionar("sin", "x") == ("sin", "", "")
    with pytest.raises(ValueError):
        texto.particionar("abc", "")
    assert texto.particionar_derecha("uno-dos-tres", "-") == ("uno-dos", "-", "tres")
    assert texto.particionar_derecha("sin", "-") == ("", "", "sin")


def test_validadores_de_texto():
    assert texto.es_alfabetico("Cobra") is True
    assert texto.es_alfabetico("cobra123") is False
    assert texto.es_alfa_numerico("Cobra123") is True
    assert texto.es_alfa_numerico("cobra!") is False
    assert texto.es_decimal("１２３") is True
    assert texto.es_decimal("Ⅷ") is False
    assert texto.es_numerico("四") is True
    assert texto.es_numerico("texto") is False
    assert texto.es_identificador("variable_1") is True
    assert texto.es_identificador("-variable") is False
    assert texto.es_imprimible("texto limpio") is True
    assert texto.es_imprimible("\u00a0") is False
    assert texto.es_ascii("ASCII") is True
    assert texto.es_ascii("ñ") is False
    assert texto.es_mayusculas("MAYÚSCULAS") is True
    assert texto.es_mayusculas("MAYUSCULA") is True
    assert texto.es_mayusculas("Mayúsculas") is False
    assert texto.es_minusculas("minúsculas") is True
    assert texto.es_minusculas("Minúsculas") is False
    assert texto.es_minusculas("123") is False
    assert texto.es_titulo("Canción De Cuna") is True
    assert texto.es_titulo("canción de cuna") is False
    assert texto.es_espacio(" \t") is True
    assert texto.es_espacio("texto") is False
    assert texto.es_digito("１２３") is True
    assert texto.es_digito("Ⅻ") is False
