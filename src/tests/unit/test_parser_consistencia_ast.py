import dataclasses
from cobra.core import Lexer
from cobra.core.parser import ClassicParser
from cobra.core.lark_parser import LarkParser
from lark import Tree


def _simplify_classic(obj):
    """Convierte el AST del parser clásico a una estructura de diccionarios."""
    mapping = {
        "NodoAsignacion": "asignacion",
        "NodoBucleMientras": "bucle_mientras",
        "NodoSwitch": "switch",
        "NodoCase": "case",
        "NodoPara": "bucle_para",
        "NodoFor": "bucle_para",
    }
    if isinstance(obj, list):
        result = []
        for item in obj:
            simplified = _simplify_classic(item)
            if simplified is not None:
                result.append(simplified)
        return result
    if dataclasses.is_dataclass(obj):
        dataclasses.asdict(obj)  # convierte nodos a dict (no usado directamente)
        name = obj.__class__.__name__
        children = []
        for field in dataclasses.fields(obj):
            value = getattr(obj, field.name)
            if isinstance(value, list):
                for v in value:
                    simplified = _simplify_classic(v)
                    if simplified is not None:
                        children.append(simplified)
            elif dataclasses.is_dataclass(value):
                simplified = _simplify_classic(value)
                if simplified is not None:
                    children.append(simplified)
        if name == "NodoFuncion":
            tipo = "funcion_asincronica" if getattr(obj, "asincronica", False) else "funcion"
            return {"type": tipo, "children": children}
        if name in mapping:
            return {"type": mapping[name], "children": children}
        if children:
            if len(children) == 1:
                return children[0]
            return {"type": "group", "children": children}
    return None


def _simplify_lark(tree):
    """Convierte el árbol de Lark a una estructura comparable."""
    if isinstance(tree, Tree):
        if tree.data in {"patron"}:
            return None
        children = [_simplify_lark(c) for c in tree.children if isinstance(c, Tree)]
        children = [c for c in children if c is not None]
        if tree.data == "cuerpo":
            if len(children) == 1:
                return children[0]
            return {"type": "group", "children": children}
        return {"type": str(tree.data), "children": children}
    return None


FRAGMENTS = [
    "var x = 1",
    "mientras 1:\n    var x = 1\nfin",
    "para i in x:\n    var a = i\nfin",
    "asincronico func f():\n    var x = 1\nfin",
    "switch x:\ncase 1:\n    var a = 2\nsino:\n    var b = 3\nfin",
]


def _parse_with_both(code: str):
    tokens = Lexer(code).analizar_token()
    classic = ClassicParser(tokens).parsear()
    lark = LarkParser(tokens).parsear()
    classic_simplified = _simplify_classic(classic)
    lark_simplified = _simplify_lark(lark)
    if isinstance(lark_simplified, dict):
        lark_simplified = [lark_simplified]
    return classic_simplified, lark_simplified


def test_parser_consistencia_ast():
    for fragment in FRAGMENTS:
        classic, lark = _parse_with_both(fragment)
        assert classic == lark
