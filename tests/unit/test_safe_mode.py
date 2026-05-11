from io import StringIO
from unittest.mock import patch

import pytest

import pcobra  # garantiza rutas para submódulos
from cobra.cli.cli import CliApplication
from cobra.core import Lexer
from cobra.core import Parser
from core.ast_nodes import NodoLlamadaFuncion, NodoValor
from core.interpreter import InterpretadorCobra
from core.semantic_validators import PrimitivaPeligrosaError


def generar_ast(codigo: str):
    tokens = Lexer(codigo).analizar_token()
    return Parser(tokens).parsear()


@pytest.mark.parametrize(
    "codigo",
    [
        "leer_archivo('x.txt')",
        "obtener_url('ejemplo')",
        "leer('x.txt')",
        "escribir('x.txt', 'hola')",
        "enviar_post('u', 'd')",
        "ejecutar(['ls'])",
        "listar_dir('.')",
    ],
)
def test_primitivas_rechazadas_en_modo_seguro(codigo):
    interp = InterpretadorCobra()
    ast = generar_ast(codigo)
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_codigo_seguro_se_ejecuta_en_modo_seguro():
    interp = InterpretadorCobra()
    nodo = NodoLlamadaFuncion("imprimir", [NodoValor("hola")])
    with patch("sys.stdout", new_callable=StringIO) as out:
        interp.ejecutar_llamada_funcion(nodo)
    assert out.getvalue().strip() == "hola"


def test_existe_no_se_habilita_solo_por_nombre_sin_usar_archivo():
    interp = InterpretadorCobra()
    ast = generar_ast('func existe(ruta) { retorno verdadero }\nimprimir(existe("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)


def test_existe_publico_desde_usar_acepta_ruta_relativa():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(existe("README.md"))')

    with patch("sys.stdout", new_callable=StringIO) as out:
        interp.ejecutar_ast(ast)

    salida = out.getvalue()
    assert "verdadero" in salida or "falso" in salida


@pytest.mark.parametrize(
    "codigo",
    [
        'usar "archivo"\nimprimir(existe("/etc/passwd"))',
        'usar "archivo"\nimprimir(existe("../secreto.txt"))',
    ],
)
def test_existe_publico_desde_usar_bloquea_rutas_fuera_de_politica(codigo):
    interp = InterpretadorCobra()
    ast = generar_ast(codigo)

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)



def test_existe_publico_no_habilita_simbolos_backend_crudos_no_publicos():
    interp = InterpretadorCobra()
    ast = generar_ast('usar "archivo"\nimprimir(leer_archivo("README.md"))')

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)

def test_cli_default_mantiene_modo_seguro_y_fallback_inseguro_deshabilitado():
    app = CliApplication()
    app.initialize()
    args = app._parse_arguments([])
    assert args.seguro is True
    assert args.allow_insecure_fallback is False


@pytest.mark.parametrize(
    "codigo",
    [
        'usar "archivo"\nimprimir(existe("./../secreto.txt"))',
        'usar "archivo"\nimprimir(existe("carpeta/../../secreto.txt"))',
    ],
)
def test_existe_publico_desde_usar_bloquea_traversal_normalizado(codigo):
    interp = InterpretadorCobra()
    ast = generar_ast(codigo)

    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(ast)

