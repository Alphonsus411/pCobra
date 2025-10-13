# -*- coding: utf-8 -*-
"""Transpilador inverso desde LaTeX a Cobra."""

from __future__ import annotations

import re
from typing import Any, List

from sympy.parsing.latex import parse_latex
from sympy.printing.pycode import pycode

from pcobra.cobra.transpilers.reverse.base import BaseReverseTranspiler
from pcobra.cobra.transpilers.reverse.from_python import ReverseFromPython


class ReverseFromLatex(BaseReverseTranspiler):
    r"""Convierte fragmentos básicos de LaTeX en nodos del AST de Cobra.

    Este conversor se enfoca en pseudocódigo escrito mediante comandos
    como ``\STATE``, ``\IF`` o ``\FOR`` presentes comúnmente en el
    entorno ``algorithmic``. Las expresiones matemáticas se convierten
    utilizando :mod:`sympy`.
    """

    def __init__(self) -> None:  # pragma: no cover - inicialización trivial
        super().__init__()
        self.python_transpiler = ReverseFromPython()

    # ------------------------------------------------------------------
    # Utilidades internas
    def _latex_expr_to_python(self, expr: str) -> str:
        """Transforma una expresión LaTeX en su equivalente en Python."""

        expr = expr.strip().strip("$")
        return pycode(parse_latex(expr))

    def _extract_braces(self, line: str) -> str:
        """Obtiene el contenido de las llaves ``{}`` de un comando LaTeX."""

        match = re.match(r"\\[A-Za-z]+\{(.*)\}", line)
        return match.group(1) if match else ""

    def _clean_identifier(self, ident: str) -> str:
        """Normaliza un identificador LaTeX removiendo escapes."""

        ident = ident.strip().strip("$")
        return ident.replace("\\", "")

    # ------------------------------------------------------------------
    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra equivalente al pseudocódigo en LaTeX."""

        python_lines: List[str] = []
        indent = 0

        for raw_line in code.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("%"):
                continue
            if line.startswith("\\begin") or line.startswith("\\end"):
                continue

            if line.startswith("\\STATE"):
                content = line[len("\\STATE") :].strip()
                if content.startswith("{") and content.endswith("}"):
                    content = content[1:-1].strip()
                if "=" in content:
                    izquierda, derecha = content.split("=", 1)
                    var = self._clean_identifier(izquierda)
                    expr = self._latex_expr_to_python(derecha)
                    python_lines.append("    " * indent + f"{var} = {expr}")
                else:
                    expr = self._latex_expr_to_python(content)
                    python_lines.append("    " * indent + expr)
                continue

            if line.startswith("\\IF"):
                condicion = self._latex_expr_to_python(self._extract_braces(line))
                python_lines.append("    " * indent + f"if {condicion}:")
                indent += 1
                continue

            if line.startswith("\\ELSE"):
                indent -= 1
                python_lines.append("    " * indent + "else:")
                indent += 1
                continue

            if line.startswith("\\ENDIF"):
                indent -= 1
                continue

            if line.startswith("\\WHILE"):
                condicion = self._latex_expr_to_python(self._extract_braces(line))
                python_lines.append("    " * indent + f"while {condicion}:")
                indent += 1
                continue

            if line.startswith("\\ENDWHILE"):
                indent -= 1
                continue

            if line.startswith("\\FOR"):
                dentro = self._extract_braces(line).replace("$", "").strip()
                if "\\TO" not in dentro:
                    raise NotImplementedError("Formato de FOR no soportado")
                parte_var, parte_fin = dentro.split("\\TO", 1)
                var, inicio = parte_var.split("=", 1)
                var = self._clean_identifier(var)
                inicio_py = self._latex_expr_to_python(inicio)
                fin_py = self._latex_expr_to_python(parte_fin)
                python_lines.append(
                    "    " * indent + f"for {var} in range({inicio_py}, {fin_py} + 1):"
                )
                indent += 1
                continue

            if line.startswith("\\ENDFOR"):
                indent -= 1
                continue

        python_code = "\n".join(python_lines)
        return self.python_transpiler.generate_ast(python_code)

