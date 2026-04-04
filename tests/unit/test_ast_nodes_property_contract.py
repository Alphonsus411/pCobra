"""Contratos de seguridad para ``property`` en nodos AST."""

from __future__ import annotations

import dis
import inspect

from pcobra.core import ast_nodes
from pcobra.core.ast_nodes import NodoAST


def _iter_nodo_classes():
    for _, cls in inspect.getmembers(ast_nodes, inspect.isclass):
        if cls.__module__ != ast_nodes.__name__:
            continue
        if not cls.__name__.startswith("Nodo"):
            continue
        if not issubclass(cls, NodoAST):
            continue
        yield cls


def test_ast_properties_are_non_recursive_and_no_eval() -> None:
    """Toda ``property`` en ``Nodo*`` debe ser O(1), no recursiva y sin evaluación."""
    violaciones: list[str] = []

    for cls in _iter_nodo_classes():
        for nombre_prop, attr in cls.__dict__.items():
            if not isinstance(attr, property) or attr.fget is None:
                continue

            fget = attr.fget
            nombres = set(fget.__code__.co_names)
            source = inspect.getsource(fget)
            instrucciones = {ins.opname for ins in dis.get_instructions(fget)}

            if {"evaluar", "evaluar_expresion"} & nombres:
                violaciones.append(
                    f"{cls.__name__}.{nombre_prop}: invoca evaluar/evaluar_expresion"
                )

            if "__dict__" in nombres or "__dict__" in source or "vars(" in source:
                violaciones.append(
                    f"{cls.__name__}.{nombre_prop}: recorre/accede __dict__ de forma dinámica"
                )

            if {"FOR_ITER", "SETUP_LOOP"} & instrucciones:
                violaciones.append(f"{cls.__name__}.{nombre_prop}: contiene bucles")

            marcadores_recorrido = (" for ", " while ", "hijo", "children", "recurs")
            if any(token in source for token in marcadores_recorrido):
                violaciones.append(
                    f"{cls.__name__}.{nombre_prop}: sugiere recorrido recursivo de hijos"
                )

    assert not violaciones, "Propiedades AST inválidas:\n- " + "\n- ".join(violaciones)
