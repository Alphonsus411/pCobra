from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.ast_nodes import (
    NodoContinuar,
    NodoIdentificador,
    NodoImprimir,
    NodoLista,
    NodoPara,
    NodoRomper,
    NodoValor,
)


def test_interprete_para_recorre_lista(capsys):
    inter = InterpretadorCobra()

    nodo = NodoPara(
        "elemento",
        NodoLista([NodoValor(1), NodoValor(2), NodoValor(3)]),
        [NodoImprimir(NodoIdentificador("elemento"))],
    )

    inter.ejecutar_nodo(nodo)

    assert capsys.readouterr().out.splitlines() == ["1", "2", "3"]


def test_interprete_para_respeta_romper(capsys):
    inter = InterpretadorCobra()

    nodo = NodoPara(
        "elemento",
        NodoLista([NodoValor(1), NodoValor(2), NodoValor(3)]),
        [
            NodoImprimir(NodoIdentificador("elemento")),
            NodoRomper(),
        ],
    )

    inter.ejecutar_nodo(nodo)

    assert capsys.readouterr().out.splitlines() == ["1"]


def test_interprete_para_respeta_continuar(capsys):
    inter = InterpretadorCobra()

    nodo = NodoPara(
        "elemento",
        NodoLista([NodoValor(1), NodoValor(2), NodoValor(3)]),
        [
            NodoContinuar(),
            NodoImprimir(NodoIdentificador("elemento")),
        ],
    )

    inter.ejecutar_nodo(nodo)

    assert capsys.readouterr().out == ""


def test_codigo_cobra_para_se_ejecuta_de_extremo_a_extremo(capsys):
    from pcobra.cobra.core import Lexer, Parser

    codigo = """
    para elemento en [1, 2, 3]:
        imprimir(elemento)
    fin
    """

    ast = Parser(Lexer(codigo).tokenizar()).parsear()

    InterpretadorCobra().ejecutar_ast(ast)

    assert capsys.readouterr().out.splitlines() == ["1", "2", "3"]
