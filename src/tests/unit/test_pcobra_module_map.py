try:
    import tomllib  # Python >= 3.11
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers import module_map
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def _write_toml(path, data):
    content = ""
    for mod, mapping in data.items():
        content += f"['{mod}']\n"
        for key, value in mapping.items():
            content += f"{key} = '{value}'\n"
    path.write_text(content)


def test_pcobra_mapeo_python(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    mod.write_text("var x = 1")
    py_out = tmp_path / "m.py"
    py_out.write_text("x = 1\n")

    mapping = {str(mod): {"python": str(py_out)}}
    toml_file = tmp_path / "pcobra.toml"
    _write_toml(toml_file, mapping)

    monkeypatch.setenv("PCOBRA_TOML", str(toml_file))
    module_map._toml_cache = None

    codigo = f"import '{mod}'\nimprimir(x)"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()

    resultado = TranspiladorPython().generate_code(ast)
    esperado = IMPORTS + f"{py_out.read_text()}print(x)\n"
    assert resultado == esperado


def test_pcobra_mapeo_js(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    mod.write_text("var x = 2")
    js_out = tmp_path / "m.js"
    js_out.write_text("let x = 2;\n")

    mapping = {str(mod): {"js": str(js_out)}}
    toml_file = tmp_path / "pcobra.toml"
    _write_toml(toml_file, mapping)

    monkeypatch.setenv("PCOBRA_TOML", str(toml_file))
    module_map._toml_cache = None

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

