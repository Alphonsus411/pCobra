from cobra.core import Token, TipoToken
from cobra.core import Parser
from core.ast_nodes import NodoCondicional, NodoOperacionBinaria, NodoFuncion, NodoLlamadaFuncion, NodoValor, NodoHolobit, NodoAsignacion, NodoBucleMientras


def test_parser_asignacion_variable():
    tokens = [
        Token(TipoToken.VAR, 'var'),
        Token(TipoToken.IDENTIFICADOR, 'x'),
        Token(TipoToken.ASIGNAR, '='),
        Token(TipoToken.ENTERO, 10),
        Token(TipoToken.EOF, None)
    ]
    parser = Parser(tokens)
    arbol = parser.parsear()

    assert isinstance(arbol[0], NodoAsignacion)
    assert arbol[0].variable == 'x'  # Comprobar que la variable es correcta
    assert isinstance(arbol[0].expresion, NodoValor)
    assert arbol[0].expresion.valor == 10  # Comprobar que el valor asignado es correcto


def test_parser_holobit():
    tokens = [
        Token(TipoToken.HOLOBIT, 'holobit'),
        Token(TipoToken.LPAREN, '('),
        Token(TipoToken.LBRACKET, '['),
        Token(TipoToken.FLOTANTE, 0.8),
        Token(TipoToken.COMA, ','),
        Token(TipoToken.FLOTANTE, -0.5),  # Cambiado a un flotante negativo
        Token(TipoToken.COMA, ','),
        Token(TipoToken.FLOTANTE, 1.2),
        Token(TipoToken.RBRACKET, ']'),
        Token(TipoToken.RPAREN, ')'),
        Token(TipoToken.EOF, None)
    ]

    parser = Parser(tokens)
    arbol = parser.parsear()

    assert isinstance(arbol[0], NodoHolobit), "Se esperaba un nodo de tipo NodoHolobit"
    assert len(arbol[0].valores) == 3, "El holobit debe contener 3 valores"
    assert arbol[0].valores[0].valor == 0.8, "El primer valor del holobit debe ser 0.8"
    assert arbol[0].valores[1].valor == -0.5, "El segundo valor del holobit debe ser -0.5"
    assert arbol[0].valores[2].valor == 1.2, "El tercer valor del holobit debe ser 1.2"


def test_parser_condicional():
    tokens = [
        Token(TipoToken.SI, 'si'),
        Token(TipoToken.IDENTIFICADOR, 'x'),
        Token(TipoToken.MAYORQUE, '>'),
        Token(TipoToken.ENTERO, 5),
        Token(TipoToken.DOSPUNTOS, ':'),
        Token(TipoToken.IDENTIFICADOR, 'proyectar'),
        Token(TipoToken.LPAREN, '('),
        Token(TipoToken.IDENTIFICADOR, 'x'),
        Token(TipoToken.COMA, ','),
        Token(TipoToken.CADENA, "'2D'"),
        Token(TipoToken.RPAREN, ')'),
        Token(TipoToken.SINO, 'sino'),
        Token(TipoToken.DOSPUNTOS, ':'),
        Token(TipoToken.IDENTIFICADOR, 'graficar'),
        Token(TipoToken.LPAREN, '('),
        Token(TipoToken.IDENTIFICADOR, 'x'),
        Token(TipoToken.RPAREN, ')'),
        Token(TipoToken.FIN, 'fin'),
        Token(TipoToken.EOF, None)
    ]
    parser = Parser(tokens)
    arbol = parser.parsear()

    assert isinstance(arbol[0], NodoCondicional)
    assert isinstance(arbol[0].condicion, NodoOperacionBinaria)
    assert arbol[0].condicion.operador.tipo == TipoToken.MAYORQUE  # Comparando el tipo de token


def test_parser_bucle_mientras():
    tokens = [
        Token(TipoToken.MIENTRAS, 'mientras'),
        Token(TipoToken.IDENTIFICADOR, 'x'),
        Token(TipoToken.MAYORQUE, '>'),
        Token(TipoToken.ENTERO, 0),
        Token(TipoToken.DOSPUNTOS, ':'),
        Token(TipoToken.IDENTIFICADOR, 'x'),
        Token(TipoToken.ASIGNAR, '='),
        Token(TipoToken.IDENTIFICADOR, 'x'),
        Token(TipoToken.RESTA, '-'),
        Token(TipoToken.ENTERO, 1),
        Token(TipoToken.FIN, 'fin'),
        Token(TipoToken.EOF, None)
    ]
    parser = Parser(tokens)
    arbol = parser.parsear()

    assert isinstance(arbol[0], NodoBucleMientras)
    assert isinstance(arbol[0].condicion, NodoOperacionBinaria)
    assert arbol[0].condicion.izquierda.valor == 'x'
    assert arbol[0].condicion.derecha.valor == 0


def test_parser_funcion():
    tokens = [
        Token(TipoToken.FUNC, 'func'),
        Token(TipoToken.IDENTIFICADOR, 'miFuncion'),
        Token(TipoToken.LPAREN, '('),
        Token(TipoToken.IDENTIFICADOR, 'x'),
        Token(TipoToken.COMA, ','),
        Token(TipoToken.IDENTIFICADOR, 'y'),
        Token(TipoToken.RPAREN, ')'),
        Token(TipoToken.DOSPUNTOS, ':'),
        Token(TipoToken.IDENTIFICADOR, 'proyectar'),
        Token(TipoToken.LPAREN, '('),
        Token(TipoToken.IDENTIFICADOR, 'x'),
        Token(TipoToken.COMA, ','),
        Token(TipoToken.CADENA, "'2D'"),
        Token(TipoToken.RPAREN, ')'),
        Token(TipoToken.FIN, 'fin'),
        Token(TipoToken.EOF, None)
    ]
    parser = Parser(tokens)
    arbol = parser.parsear()

    assert isinstance(arbol[0], NodoFuncion)  # Verifica que es una función
    assert arbol[0].nombre == 'miFuncion'  # Verifica el nombre de la función

    # Verifica que el cuerpo contenga una llamada a función (proyectar)
    assert isinstance(arbol[0].cuerpo[0], NodoLlamadaFuncion)
    assert arbol[0].cuerpo[0].nombre == 'proyectar'
    assert isinstance(arbol[0].cuerpo[0].argumentos[0], NodoValor)
    assert arbol[0].cuerpo[0].argumentos[0].valor == 'x'
    assert arbol[0].cuerpo[0].argumentos[1].valor == "'2D'"
