# -*- coding: utf-8 -*-
"""Transpilador inverso desde ensamblador a Cobra."""

from __future__ import annotations

import re
from typing import Any, List

from cobra.transpilers.reverse.base import BaseReverseTranspiler
from cobra.core.ast_nodes import NodoAsignacion, NodoIdentificador, NodoValor


def _parse_expression(text: str) -> Any:
    """Convierte operandos de ensamblador a nodos del AST."""
    texto = text.strip()
    try:
        return NodoValor(int(texto))
    except ValueError:
        try:
            return NodoValor(float(texto))
        except ValueError:
            return NodoIdentificador(texto)


class ReverseFromASM(BaseReverseTranspiler):
    """Transpilador inverso de ensamblador a Cobra."""

    MOV_RE = re.compile(r"^MOV\s+([A-Za-z0-9_]+),\s*([A-Za-z0-9_]+)$", re.IGNORECASE)

    def generate_ast(self, code: str) -> List[Any]:
        """Genera nodos Cobra a partir de instrucciones `MOV`."""

        ast: List[Any] = []
        for raw in code.splitlines():
            line = raw.strip()
            if not line:
                continue
            match = self.MOV_RE.match(line)
            if match:
                destino, valor = match.groups()
                ast.append(
                    NodoAsignacion(
                        NodoIdentificador(destino), _parse_expression(valor)
                    )
                )
        self.ast = ast
        return ast

