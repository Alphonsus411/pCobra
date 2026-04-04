from __future__ import annotations

import ast
from pathlib import Path


ARCHIVO_AST_NODES = Path("src/pcobra/core/ast_nodes.py")
ATRIBUTOS_SUBARBOL = {
    "izquierda",
    "derecha",
    "expresion",
    "cuerpo",
    "bloque_si",
    "bloque_sino",
    "bloque_try",
    "bloque_catch",
    "bloque_finally",
    "instrucciones",
    "elementos",
    "casos",
    "por_defecto",
}


def _decorador_dataclass(nodo_clase: ast.ClassDef) -> ast.Call | ast.Name | None:
    for decorador in nodo_clase.decorator_list:
        if isinstance(decorador, ast.Name) and decorador.id == "dataclass":
            return decorador
        if isinstance(decorador, ast.Call) and isinstance(decorador.func, ast.Name) and decorador.func.id == "dataclass":
            return decorador
    return None


def _tiene_repr_false(decorador: ast.Call | ast.Name | None) -> bool:
    if isinstance(decorador, ast.Call):
        for kw in decorador.keywords:
            if kw.arg == "repr" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                return True
    return False


def test_politica_repr_nodos_ast() -> None:
    arbol = ast.parse(ARCHIVO_AST_NODES.read_text(encoding="utf-8"))

    clases_nodo = [
        nodo
        for nodo in arbol.body
        if isinstance(nodo, ast.ClassDef) and nodo.name.startswith("Nodo") and nodo.name != "NodoAST"
    ]

    for clase in clases_nodo:
        decorador = _decorador_dataclass(clase)
        if decorador is None:
            continue

        metodo_repr = next(
            (item for item in clase.body if isinstance(item, ast.FunctionDef) and item.name == "__repr__"),
            None,
        )

        assert _tiene_repr_false(decorador) or metodo_repr is not None, (
            f"{clase.name} debe usar @dataclass(repr=False) o definir __repr__ corto"
        )

        if metodo_repr is not None:
            texto_repr = ast.get_source_segment(ARCHIVO_AST_NODES.read_text(encoding="utf-8"), metodo_repr) or ""
            assert "<" in texto_repr and "id(self)" in texto_repr, (
                f"{clase.name}.__repr__ debe usar formato corto con id"
            )
            for atributo in ATRIBUTOS_SUBARBOL:
                assert atributo not in texto_repr, (
                    f"{clase.name}.__repr__ no debe serializar subárboles ({atributo})"
                )

        metodo_str = next(
            (item for item in clase.body if isinstance(item, ast.FunctionDef) and item.name == "__str__"),
            None,
        )
        if metodo_str is not None:
            texto_str = ast.get_source_segment(ARCHIVO_AST_NODES.read_text(encoding="utf-8"), metodo_str) or ""
            assert "__repr__" in texto_str, f"{clase.name}.__str__ debe delegar a __repr__"
