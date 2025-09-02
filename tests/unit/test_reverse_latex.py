from cobra.transpilers.reverse.from_latex import ReverseFromLatex
from core.ast_nodes import (
    NodoAsignacion,
    NodoBucleMientras,
    NodoCondicional,
    NodoPara,
)


def test_reverse_from_latex_conditional():
    codigo = r"""
    \begin{algorithmic}
    \STATE $x = a + b$
    \IF{$x > 0$}
        \STATE $y = x - 1$
    \ENDIF
    \end{algorithmic}
    """

    ast = ReverseFromLatex().generate_ast(codigo)
    assert len(ast) == 2
    assert isinstance(ast[0], NodoAsignacion)
    cond = ast[1]
    assert isinstance(cond, NodoCondicional)
    assert isinstance(cond.bloque_si[0], NodoAsignacion)


def test_reverse_from_latex_loops():
    codigo = r"""
    \begin{algorithmic}
    \FOR{$i=1 \TO n$}
        \STATE $s = s + i$
    \ENDFOR
    \WHILE{$s > 0$}
        \STATE $s = s - 1$
    \ENDWHILE
    \end{algorithmic}
    """

    ast = ReverseFromLatex().generate_ast(codigo)
    assert len(ast) == 2
    ciclo_for = ast[0]
    assert isinstance(ciclo_for, NodoPara)
    assert isinstance(ciclo_for.cuerpo[0], NodoAsignacion)
    ciclo_while = ast[1]
    assert isinstance(ciclo_while, NodoBucleMientras)
    assert isinstance(ciclo_while.cuerpo[0], NodoAsignacion)

