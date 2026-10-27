import shutil
import subprocess

import pytest

from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import Parser
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript


def transpilar(source):
    ast = Parser(Lexer(source).analizar_token()).parsear()
    return TranspiladorJavaScript().generate_code(ast)


def test_import_historico_no_cambia_sin_colision():
    code = transpilar('imprimir("Hola")')
    assert "import * as numero from './nativos/numero.js';" in code


def test_variable_numero_no_colisiona_con_import():
    code = transpilar("var numero = 6\nimprimir(numero + 4)")
    assert "import * as __pcobra_numero from './nativos/numero.js';" in code
    assert "let numero = 6;" in code
    if not shutil.which("node"):
        pytest.skip("Node no está disponible")
    checked = subprocess.run(
        ["node", "--input-type=module", "--check"],
        input=code,
        capture_output=True,
        text=True,
    )
    assert checked.returncode == 0, checked.stderr


def test_alias_interno_no_colisiona_con_identificador_del_programa():
    code = transpilar("var __pcobra_numero = 1\nvar numero = 6\nimprimir(numero)")
    assert "import * as __pcobra_numero_ from './nativos/numero.js';" in code
