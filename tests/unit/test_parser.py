import pytest
from cobra.core import Parser
from core.ast_nodes import NodoAsignacion, NodoHolobit, NodoCondicional
from cobra.core import Lexer


@pytest.mark.timeout(5)  # Timeout de 5 segundos para evitar bucles infinitos
def test_parser_asignacion_variable():
    """
    Test para validar la asignación de una variable con un holobit.
    """
    # Entrada de código fuente
    codigo = 'var x = holobit([0.8, -0.5, 1.2])'

    # Inicializar el lexer para obtener los tokens
    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()  # Cambiar 'tokenizar' por 'analizar_token'

    # Inicializar el parser con los tokens
    parser = Parser(tokens)

    # Ejecutar el parser
    try:
        arbol = parser.parsear()
        assert arbol is not None, "El árbol sintáctico es None, el parser falló."

        # Verificar que el primer nodo de la lista es de tipo 'NodoAsignacion'
        primer_nodo = arbol[0]  # Accedemos al primer nodo de la lista
        assert isinstance(primer_nodo,
                          NodoAsignacion), f"Se esperaba NodoAsignacion, pero se encontró {type(primer_nodo).__name__}"

        # Validar que la variable asignada es 'x'
        assert primer_nodo.variable == 'x', f"Se esperaba 'x', pero se encontró {primer_nodo.variable}"

        # Validar que la expresión es un holobit con los valores correctos
        assert isinstance(primer_nodo.expresion, NodoHolobit), "Se esperaba un NodoHolobit en la expresión"
        assert [nodo.valor for nodo in primer_nodo.expresion.valores] == [0.8, -0.5,
                                                                          1.2], f"Se esperaban los valores [0.8, -0.5, 1.2], pero se encontraron {primer_nodo.expresion.valores}"

    except Exception as e:
        pytest.fail(f"Error en el parser: {e}")


@pytest.mark.timeout(5)  # Timeout de 5 segundos para evitar bucles infinitos
def test_parser_condicional_si_sino():
    """
    Test para validar una estructura condicional con si/sino.
    """
    # Entrada de código fuente con una estructura condicional
    codigo = '''
    var x = 10
    si x > 5 :
        proyectar(x, "2D")
    sino :
        graficar(x)
    fin
    '''

    # Inicializamos el lexer
    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()
    print(f"Tokens generados: {tokens}")  # Imprimir los tokens generados

    # Inicializamos el parser con los tokens
    parser = Parser(tokens)

    # Ejecutar el parser
    try:
        arbol = parser.parsear()
        assert arbol is not None, "El árbol sintáctico es None, el parser falló."
        # Verificar que el nodo raíz es de tipo 'NodoCondicional'
        assert isinstance(arbol[0], NodoCondicional), f"Se esperaba 'NodoCondicional', pero se encontró {type(arbol[0]).__name__}"

    except RecursionError:
        pytest.fail("El parser ha entrado en una recursión infinita.")
    except Exception as e:
        pytest.fail(f"Error en el parser: {e}")
