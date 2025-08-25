import pytest
import backend  # garantiza rutas para submódulos
from cobra.core import Lexer
from cobra.core import Parser
from core.interpreter import InterpretadorCobra
from core.ast_nodes import NodoLlamadaFuncion, NodoValor
from core.semantic_validators import PrimitivaPeligrosaError


def generar_ast(codigo: str):
    tokens = Lexer(codigo).analizar_token()
    return Parser(tokens).parsear()


codigo_base = "import 'os'\nimport 'sys'"
base_ast = generar_ast(codigo_base)
EXTRA_NODOS = [
    NodoLlamadaFuncion("__import__", [NodoValor("os")]),
    NodoLlamadaFuncion("exec", [NodoValor("1")]),
]
AST_COMPLETO = base_ast + EXTRA_NODOS


def test_imports_y_reflexion_en_modo_seguro(tmp_path, monkeypatch):
    import sys
    mod = sys.modules['core.interpreter']
    monkeypatch.setattr(mod, 'MODULES_PATH', str(tmp_path))
    monkeypatch.setattr(mod, 'IMPORT_WHITELIST', {
        str(tmp_path / 'os'),
        str(tmp_path / 'sys'),
    })
    ruta_os = tmp_path / 'os'
    ruta_sys = tmp_path / 'sys'
    ruta_os.write_text('')
    ruta_sys.write_text('')
    AST_COMPLETO[0].ruta = str(ruta_os)
    AST_COMPLETO[1].ruta = str(ruta_sys)
    interp = InterpretadorCobra()
    with pytest.raises(PrimitivaPeligrosaError):
        interp.ejecutar_ast(AST_COMPLETO)


def test_imports_y_reflexion_fuera_modo_seguro(tmp_path, monkeypatch):
    import sys
    mod = sys.modules['core.interpreter']
    monkeypatch.setattr(mod, 'MODULES_PATH', str(tmp_path))
    monkeypatch.setattr(mod, 'IMPORT_WHITELIST', {
        str(tmp_path / 'os'),
        str(tmp_path / 'sys'),
    })
    ruta_os = tmp_path / 'os'
    ruta_sys = tmp_path / 'sys'
    ruta_os.write_text('')
    ruta_sys.write_text('')
    AST_COMPLETO[0].ruta = str(ruta_os)
    AST_COMPLETO[1].ruta = str(ruta_sys)
    interp = InterpretadorCobra(safe_mode=False)
    interp.ejecutar_ast(AST_COMPLETO)
