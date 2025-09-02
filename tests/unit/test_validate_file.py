import os
import sys
import types
from types import SimpleNamespace

import pytest


def _stub_dependencies():
    """Crea stubs mínimos para importar ``compile_cmd`` sin dependencias pesadas."""
    transpilers_pkg = types.ModuleType("cobra.transpilers")
    transpilers_pkg.module_map = SimpleNamespace(get_toml_map=lambda: {})
    sys.modules.setdefault("cobra.transpilers", transpilers_pkg)
    sys.modules.setdefault("cobra.transpilers.transpiler", types.ModuleType("cobra.transpilers.transpiler"))

    transpiler_classes = {
        "to_asm": "TranspiladorASM",
        "to_c": "TranspiladorC",
        "to_cobol": "TranspiladorCOBOL",
        "to_cpp": "TranspiladorCPP",
        "to_fortran": "TranspiladorFortran",
        "to_go": "TranspiladorGo",
        "to_java": "TranspiladorJava",
        "to_kotlin": "TranspiladorKotlin",
        "to_js": "TranspiladorJavaScript",
        "to_julia": "TranspiladorJulia",
        "to_latex": "TranspiladorLatex",
        "to_matlab": "TranspiladorMatlab",
        "to_mojo": "TranspiladorMojo",
        "to_pascal": "TranspiladorPascal",
        "to_php": "TranspiladorPHP",
        "to_perl": "TranspiladorPerl",
        "to_visualbasic": "TranspiladorVisualBasic",
        "to_python": "TranspiladorPython",
        "to_r": "TranspiladorR",
        "to_ruby": "TranspiladorRuby",
        "to_rust": "TranspiladorRust",
        "to_wasm": "TranspiladorWasm",
        "to_swift": "TranspiladorSwift",
    }
    for mod, cls in transpiler_classes.items():
        module_name = f"cobra.transpilers.transpiler.{mod}"
        module = types.ModuleType(module_name)
        setattr(module, cls, type(cls, (), {}))
        sys.modules[module_name] = module

    ast_cache = types.ModuleType("core.ast_cache")
    ast_cache.obtener_ast = lambda _code: []
    sys.modules["core.ast_cache"] = ast_cache

    sandbox = types.ModuleType("core.sandbox")
    sandbox.validar_dependencias = lambda *_, **__: None
    sys.modules["core.sandbox"] = sandbox

    sem_validators = types.ModuleType("core.semantic_validators")
    class PrimitivaPeligrosaError(Exception):
        pass
    sem_validators.PrimitivaPeligrosaError = PrimitivaPeligrosaError
    sem_validators.construir_cadena = lambda: SimpleNamespace(visit=lambda _self, _nodo: None)
    sys.modules["core.semantic_validators"] = sem_validators

    base_cmd = types.ModuleType("cobra.cli.commands.base")
    base_cmd.BaseCommand = type("BaseCommand", (), {})
    sys.modules["cobra.cli.commands.base"] = base_cmd

    i18n = types.ModuleType("cobra.cli.i18n")
    i18n._ = lambda s: s
    sys.modules["cobra.cli.i18n"] = i18n

    msgs = types.ModuleType("cobra.cli.utils.messages")
    msgs.mostrar_error = lambda _msg: None
    msgs.mostrar_info = lambda _msg: None
    sys.modules["cobra.cli.utils.messages"] = msgs

    cobra_core = types.ModuleType("cobra.core")
    cobra_core.ParserError = Exception
    sys.modules["cobra.core"] = cobra_core


_stub_dependencies()

from cobra.cli.commands.compile_cmd import MAX_FILE_SIZE, validate_file


def test_validate_file_nonexistent(tmp_path):
    """Debe fallar si el archivo no existe."""
    ruta_invalida = tmp_path / "inexistente.cobra"
    with pytest.raises(ValueError):
        validate_file(str(ruta_invalida))


def test_validate_file_no_read_permission(tmp_path, monkeypatch):
    """Debe fallar si no hay permisos de lectura."""
    archivo = tmp_path / "sin_permiso.cobra"
    archivo.write_text("contenido")
    os.chmod(archivo, 0)

    monkeypatch.setattr(os, "access", lambda *_: False)

    with pytest.raises(ValueError):
        validate_file(str(archivo))


def test_validate_file_too_large(tmp_path):
    """Debe fallar si el archivo excede el tamaño permitido."""
    archivo = tmp_path / "grande.cobra"
    with open(archivo, "wb") as f:
        f.seek(MAX_FILE_SIZE)
        f.write(b"0")

    with pytest.raises(ValueError):
        validate_file(str(archivo))


def test_validate_file_ok(tmp_path):
    """Devuelve ``True`` para un archivo válido."""
    archivo = tmp_path / "valido.cobra"
    archivo.write_text("imprimir('hola')\n")
    assert validate_file(str(archivo)) is True
