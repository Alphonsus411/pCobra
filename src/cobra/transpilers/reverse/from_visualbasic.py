# -*- coding: utf-8 -*-
"""Transpilador inverso desde VisualBasic a Cobra."""

from __future__ import annotations

import re
from typing import Any, List

from cobra.transpilers.reverse.base import BaseReverseTranspiler
from core.ast_nodes import NodoAsignacion, NodoIdentificador, NodoValor


def _parse_expression(text: str) -> Any:
    """Convierte una expresión textual en un nodo del AST de Cobra."""
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


class ReverseFromVisualBasic(BaseReverseTranspiler):
    """Transpilador inverso de VisualBasic a Cobra."""

    ASSIGN_RE = re.compile(
        r"^(?:Dim\s+)?([A-Za-z_][\w]*)\s*(?:As\s+\w+)?\s*=\s*(.+)$",
        re.IGNORECASE,
    )

    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra desde código VisualBasic."""

        ast: List[Any] = []
        for raw in code.splitlines():
            line = raw.strip()
            if not line or line.startswith("'"):
                continue
            match = self.ASSIGN_RE.match(line)
            if match:
                nombre, valor = match.groups()
                ast.append(
                    NodoAsignacion(
                        NodoIdentificador(nombre), _parse_expression(valor)
                    )
                )
        self.ast = ast
        return ast

