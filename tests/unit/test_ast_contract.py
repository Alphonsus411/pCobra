from __future__ import annotations

import pytest

from core.ast_nodes import NodoCondicional, NodoValor
from core.utils import ErrorEstructuraAST, validar_ast_estructural


def test_ast_falla_si_hay_lista_donde_se_espera_nodo_bloque() -> None:
    nodo = NodoCondicional(NodoValor(True), [NodoValor(1)], [NodoValor(0)])
    nodo.bloque_si = [NodoValor(1)]  # inyección inválida deliberada

    with pytest.raises(ErrorEstructuraAST, match="Se encontró lista donde se esperaba NodoBloque"):
        validar_ast_estructural([nodo])
