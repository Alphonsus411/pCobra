import ast
from pathlib import Path


def _leer_ast(relpath: str) -> ast.Module:
    ruta = Path(__file__).resolve().parents[2] / relpath
    return ast.parse(ruta.read_text(encoding="utf-8"))


def _extraer_all(modulo: ast.Module) -> set[str]:
    for nodo in modulo.body:
        if isinstance(nodo, ast.Assign):
            for target in nodo.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(nodo.value, (ast.List, ast.Tuple)):
                        return {elt.value for elt in nodo.value.elts if isinstance(elt, ast.Constant)}
    return set()


def _nombres_funciones(modulo: ast.Module) -> set[str]:
    return {n.name for n in modulo.body if isinstance(n, ast.FunctionDef)}


def test_corelibs_logica_api_espanola_publica():
    modulo = _leer_ast("src/pcobra/corelibs/logica.py")
    exports = _extraer_all(modulo)
    assert "coalescer" in exports
    assert "coalesce" not in exports


def test_standard_library_logica_api_espanola_publica():
    modulo = _leer_ast("src/pcobra/standard_library/logica.py")
    exports = _extraer_all(modulo)
    funciones = _nombres_funciones(modulo)
    assert "coalescer" in exports
    assert "coalesce" not in exports
    assert "_coalesce_interno" in funciones
    assert "coalesce" not in funciones
