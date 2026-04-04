"""Pruebas de guardia para evitar stringificación de nodos en `ejecutar_nodo`.

Objetivo:
prevenir recursión infinita *antes* del evaluador, impidiendo trazas que
serialicen nodos completos (`str`/`repr`/f-string directo de `nodo` o
`expresion`).
"""

from __future__ import annotations

import ast
import inspect
import textwrap

from pcobra.core.interpreter import InterpretadorCobra


FORBIDDEN_PATTERNS = (
    "print(nodo)",
    "print(expresion)",
    'f"{nodo}"',
    "f'{nodo}'",
    'f"{expresion}"',
    "f'{expresion}'",
    "repr(nodo)",
    "repr(expresion)",
)


class _PrintNodoExpresionVisitor(ast.NodeVisitor):
    """Valida que `print(...)` solo use `nodo/expresion` vía `type` e `id`."""

    def __init__(self) -> None:
        self.violations: list[str] = []
        self._stack: list[ast.AST] = []

    def generic_visit(self, node: ast.AST) -> None:
        self._stack.append(node)
        super().generic_visit(node)
        self._stack.pop()

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            for arg in node.args:
                self._scan_print_arg(arg)
        self.generic_visit(node)

    def _scan_print_arg(self, arg: ast.AST) -> None:
        for child in ast.walk(arg):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id == "repr" and child.args:
                    if _is_name(child.args[0], {"nodo", "expresion"}):
                        self.violations.append("Uso de repr(...) con nodo/expresion en print")
            if isinstance(child, ast.Name) and child.id in {"nodo", "expresion"}:
                if not _is_name_used_in_allowed_wrapper(arg, child):
                    self.violations.append(
                        f"Uso directo de '{child.id}' en print; solo se permite type(...).__name__ o id(...)"
                    )


def _is_name(node: ast.AST | None, names: set[str]) -> bool:
    return isinstance(node, ast.Name) and node.id in names


def _is_name_used_in_allowed_wrapper(scope: ast.AST, target: ast.Name) -> bool:
    """Indica si `target` está cubierto por `type(target)` o `id(target)`."""
    for parent in ast.walk(scope):
        if not isinstance(parent, ast.Call) or not isinstance(parent.func, ast.Name):
            continue
        if parent.func.id not in {"type", "id"} or not parent.args:
            continue
        if parent.args[0] is target:
            return True
    return False


def _source_ejecutar_nodo() -> str:
    raw = inspect.getsource(InterpretadorCobra.ejecutar_nodo)
    return textwrap.dedent(raw)


def _source_nodo_imprimir_branch(src: str) -> str:
    start = src.find("elif isinstance(nodo, NodoImprimir):")
    assert start != -1, "No se encontró la rama NodoImprimir en ejecutar_nodo"

    rest = src[start:]
    next_elif = rest.find("\n        elif isinstance(", 1)
    if next_elif == -1:
        return rest
    return rest[:next_elif]


def test_ejecutar_nodo_no_contiene_stringify_peligroso_literal() -> None:
    src = _source_ejecutar_nodo()

    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in src, f"Patrón peligroso detectado en ejecutar_nodo: {pattern}"


def test_ejecutar_nodo_prints_solo_type_name_e_id_para_nodo_y_expresion() -> None:
    src = _source_ejecutar_nodo()
    tree = ast.parse(src)

    visitor = _PrintNodoExpresionVisitor()
    visitor.visit(tree)

    assert not visitor.violations, " | ".join(visitor.violations)


def test_rama_nodo_imprimir_no_usa_repr_de_nodo_ni_expresion() -> None:
    src = _source_ejecutar_nodo()
    branch = _source_nodo_imprimir_branch(src)

    assert "repr(nodo)" not in branch
    assert "repr(expresion)" not in branch
