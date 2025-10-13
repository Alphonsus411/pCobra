# -*- coding: utf-8 -*-
"""Transpilador inverso desde COBOL a Cobra."""

from __future__ import annotations

import re
from typing import Any, List

from pcobra.cobra.transpilers.reverse.base import BaseReverseTranspiler
from pcobra.cobra.core.ast_nodes import NodoAsignacion, NodoIdentificador, NodoValor


def _parse_expression(text: str) -> Any:
    """Convierte texto COBOL en un nodo del AST de Cobra."""
    texto = text.strip()
    if texto.startswith(("'", '"')) and texto.endswith(("'", '"')):
        return NodoValor(texto[1:-1])
    try:
        return NodoValor(int(texto))
    except ValueError:
        try:
            return NodoValor(float(texto))
        except ValueError:
            return NodoIdentificador(texto)


class ReverseFromCOBOL(BaseReverseTranspiler):
    """Transpilador inverso de COBOL a Cobra."""

    ASSIGN_RE = re.compile(
        r"^MOVE\s+(.+)\s+TO\s+([A-Za-z0-9_-]+)",
        re.IGNORECASE,
    )

    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra equivalente al código COBOL."""

        ast: List[Any] = []
        for raw in code.splitlines():
            line = raw.strip()
            if line.endswith('.'):
                line = line[:-1]
            match = self.ASSIGN_RE.match(line)
            if match:
                valor, nombre = match.groups()
                ast.append(
                    NodoAsignacion(
                        NodoIdentificador(nombre), _parse_expression(valor)
                    )
                )
        self.ast = ast
        return ast

