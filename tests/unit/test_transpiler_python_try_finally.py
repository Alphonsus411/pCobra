from contextlib import redirect_stdout
from io import StringIO

import pytest

from pcobra.core.ast_nodes import (
    NodoBloque,
    NodoFor,
    NodoFuncion,
    NodoIdentificador,
    NodoImportDesde,
    NodoImprimir,
    NodoInstancia,
    NodoLlamadaFuncion,
    NodoPasar,
    NodoThrow,
    NodoTryCatch,
    NodoValor,
    NodoWith,
)
from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import Parser
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.core.interpreter import InterpretadorCobra


def _transpilar_y_compilar(nodo):
    codigo = TranspiladorPython().generate_code([nodo])
    compile(codigo, "<pcobra-test>", "exec")
    return codigo


@pytest.mark.parametrize(
    ("nodo", "clausulas_esperadas", "incluye_except"),
    [
        (
            NodoTryCatch(
                [NodoThrow(NodoValor("fallo"))],
                "e",
                [NodoImprimir(NodoIdentificador("e"))],
            ),
            ("try:\n", "except Exception as e:\n"),
            True,
        ),
        (
            NodoTryCatch(
                [NodoImprimir(NodoValor("trabajo"))],
                bloque_finally=[NodoImprimir(NodoValor("limpieza"))],
            ),
            ("try:\n", "finally:\n"),
            False,
        ),
        (
            NodoTryCatch(
                [NodoThrow(NodoValor("fallo"))],
                "e",
                [NodoImprimir(NodoIdentificador("e"))],
                [NodoImprimir(NodoValor("limpieza"))],
            ),
            (
                "try:\n",
                "except Exception as __cobra_excepcion_temporal:\n",
                "finally:\n",
            ),
            True,
        ),
    ],
    ids=("try-catch", "try-finally", "try-catch-finally"),
)
def test_transpila_variantes_try_validas(nodo, clausulas_esperadas, incluye_except):
    codigo = _transpilar_y_compilar(nodo)

    posiciones = [codigo.index(clausula) for clausula in clausulas_esperadas]
    assert posiciones == sorted(posiciones)
    assert ("except " in codigo) is incluye_except


@pytest.mark.parametrize(
    "fuente",
    [
        """
intentar:
    imprimir("trabajo")
finalmente:
    imprimir("limpieza")
fin
""",
        """
intentar:
    lanzar "fallo"
capturar e:
    imprimir(e)
finalmente:
    imprimir("limpieza")
fin
""",
    ],
    ids=("try-finally", "try-catch-finally"),
)
def test_e2e_fuente_cobra_try_finally_genera_python_valido(fuente):
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    compile(codigo, "<pcobra-test>", "exec")
    assert "try:\n" in codigo
    assert "finally:\n" in codigo


def _ejecutar_python(codigo):
    return _ejecutar_python_en_espacio(codigo, {})


def _ejecutar_python_en_espacio(codigo, espacio):
    salida = StringIO()
    compilado = compile(codigo, "<pcobra-test>", "exec")
    with redirect_stdout(salida):
        exec(compilado, espacio)
    return salida.getvalue()


def test_fuente_cobra_capturar_conserva_excepcion_durante_finalmente():
    fuente = """
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()
    salida_interprete = StringIO()
    with redirect_stdout(salida_interprete):
        InterpretadorCobra().ejecutar_ast(ast)

    codigo = TranspiladorPython().generate_code(ast)

    assert _ejecutar_python(codigo) == salida_interprete.getvalue() == "fallo\nfallo\n"


def test_nombre_temporal_no_colisiona_con_identificador_cobra():
    fuente = """
var __cobra_excepcion_temporal = "usuario"
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(__cobra_excepcion_temporal)
    imprimir(error)
fin
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    assert "except Exception as __cobra_excepcion_temporal_1:" in codigo
    assert _ejecutar_python(codigo) == "fallo\nusuario\nfallo\n"


def test_nombre_temporal_no_colisiona_con_referencia_cobra_futura():
    fuente = """
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
imprimir(__cobra_excepcion_temporal)
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    transpilador = TranspiladorPython()
    codigo = transpilador.generate_code(ast)
    codigo_repetido = transpilador.generate_code(ast)

    assert codigo == codigo_repetido
    assert "except Exception as __cobra_excepcion_temporal_1:" in codigo
    espacio = {"__cobra_excepcion_temporal": "usuario"}
    assert _ejecutar_python_en_espacio(codigo, espacio) == "fallo\nfallo\nusuario\n"


def test_nombre_temporal_evade_varias_referencias_cobra_futuras():
    fuente = """
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
imprimir(__cobra_excepcion_temporal)
imprimir(__cobra_excepcion_temporal_1)
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    assert "except Exception as __cobra_excepcion_temporal_2:" in codigo
    espacio = {
        "__cobra_excepcion_temporal": "usuario",
        "__cobra_excepcion_temporal_1": "usuario 1",
    }
    assert _ejecutar_python_en_espacio(codigo, espacio) == (
        "fallo\nfallo\nusuario\nusuario 1\n"
    )


def test_nombre_destino_llamada_no_se_usa_como_temporal():
    """FALLA EN BASE: el alias de ``except`` borraba la función; PASA EN HEAD."""
    fuente = """
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
imprimir(__cobra_excepcion_temporal)
__cobra_excepcion_temporal_1()
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    transpilador = TranspiladorPython()
    codigo = transpilador.generate_code(ast)
    codigo_repetido = transpilador.generate_code(ast)

    assert codigo == codigo_repetido
    assert "except Exception as __cobra_excepcion_temporal_2:" in codigo

    def destino_llamada():
        print("llamada conservada")

    espacio = {
        "__cobra_excepcion_temporal": "usuario",
        "__cobra_excepcion_temporal_1": destino_llamada,
    }
    assert _ejecutar_python_en_espacio(codigo, espacio) == (
        "fallo\nfallo\nusuario\nllamada conservada\n"
    )


def test_literal_en_bloque_intentar_no_reserva_nombre_temporal():
    fuente = """
intentar:
    imprimir("__cobra_excepcion_temporal")
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    assert "except Exception as __cobra_excepcion_temporal:" in codigo
    assert _ejecutar_python(codigo) == ("__cobra_excepcion_temporal\nfallo\nfallo\n")


def test_recolector_cubre_categorias_estructurales_de_identificadores():
    nodos = [
        NodoFuncion("funcion_usuario", ["parametro_usuario"], NodoBloque()),
        NodoFor("variable_bucle", NodoValor([]), [NodoPasar()]),
        NodoWith(NodoIdentificador("contexto_usuario"), "alias_usuario", NodoBloque()),
        NodoImportDesde("modulo.usuario", "simbolo_usuario", "importado_usuario"),
        NodoInstancia("ClaseUsuario"),
        NodoLlamadaFuncion("destino_usuario", []),
    ]

    nombres = TranspiladorPython()._recopilar_nombres_identificadores(nodos)

    assert {
        "funcion_usuario",
        "parametro_usuario",
        "variable_bucle",
        "contexto_usuario",
        "alias_usuario",
        "simbolo_usuario",
        "importado_usuario",
        "ClaseUsuario",
        "destino_usuario",
    } <= nombres
    assert "modulo.usuario" not in nombres


def test_literal_futuro_no_reserva_nombre_temporal():
    fuente = """
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
imprimir("__cobra_excepcion_temporal")
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    assert "except Exception as __cobra_excepcion_temporal:" in codigo
    assert _ejecutar_python(codigo) == ("fallo\nfallo\n__cobra_excepcion_temporal\n")


def test_fuente_cobra_sin_excepcion_omite_capturar():
    fuente = """
intentar:
    imprimir("correcto")
capturar error:
    imprimir(error)
finalmente:
    imprimir("limpieza")
fin
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    assert _ejecutar_python(codigo) == "correcto\nlimpieza\n"
