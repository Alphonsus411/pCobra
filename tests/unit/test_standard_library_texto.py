import pytest

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


def test_prefijos_y_sufijos():
    assert texto.quitar_prefijo("🧪Prueba", "🧪") == "Prueba"
    assert texto.quitar_prefijo("demo", "x") == "demo"
    assert texto.quitar_sufijo("archivo.log", ".log") == "archivo"
    assert texto.quitar_sufijo("archivo.log", ".gz") == "archivo.log"


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


def test_centrar_rellenar_y_casefold():
    assert texto.centrar_texto("cobra", 9, "*") == "**cobra**"
    with pytest.raises(TypeError):
        texto.centrar_texto("cobra", 10, "--")
    assert texto.rellenar_ceros("-5", 4) == "-005"
    assert texto.rellenar_ceros("猫", 3) == "00猫"
    assert texto.minusculas_casefold("Straße") == "strasse"
