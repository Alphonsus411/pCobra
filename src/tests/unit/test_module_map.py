import yaml
from unittest.mock import patch

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers import module_map
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def test_transpilador_mapeo_python(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    mod.write_text("var x = 1")
    py_out = tmp_path / "m.py"
    py_out.write_text("x = 1\n")

    mapping = {str(mod): {"version": "0.1.0", "python": str(py_out)}}
    mapfile = tmp_path / "cobra.mod"
    mapfile.write_text(yaml.safe_dump(mapping))

    monkeypatch.setenv("COBRA_MODULE_MAP", str(mapfile))
    module_map._cache = None

    codigo = f"import '{mod}'\nimprimir(x)"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()

    resultado = TranspiladorPython().generate_code(ast)
    esperado = IMPORTS + f"{py_out.read_text()}print(x)\n"
    assert resultado == esperado


def test_transpilador_mapeo_js(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    mod.write_text("var x = 2")
    js_out = tmp_path / "m.js"
    js_out.write_text("let x = 2;\n")

    mapping = {str(mod): {"version": "0.1.0", "js": str(js_out)}}
    mapfile = tmp_path / "cobra.mod"
    mapfile.write_text(yaml.safe_dump(mapping))

    monkeypatch.setenv("COBRA_MODULE_MAP", str(mapfile))
    module_map._cache = None

    codigo = f"import '{mod}'\nimprimir(x)"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()

    resultado = TranspiladorJavaScript().generate_code(ast)
    esperado = (
        "import * as io from './nativos/io.js';\n"
        + "import * as net from './nativos/io.js';\n"
        + "import * as matematicas from './nativos/matematicas.js';\n"
        + "import { Pila, Cola } from './nativos/estructuras.js';\n"
        + "let x = 2;\n"
        + "console.log(x);"
    )
    assert resultado == esperado
