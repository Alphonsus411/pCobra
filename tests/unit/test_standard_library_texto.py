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
