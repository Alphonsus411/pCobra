import sys
from types import SimpleNamespace

import pytest

import core.ast_nodes as core_ast_nodes

# Asegura que los transpiladores usen el módulo completo de nodos AST
sys.modules["cobra.core.ast_nodes"] = core_ast_nodes

from cobra.cli.commands.compile_cmd import CompileCommand


@pytest.mark.timeout(5)
def test_transpilador_inexistente(monkeypatch, tmp_path):
    archivo = tmp_path / "code.co"
    archivo.write_text("x = 1")
    mensajes = []

    monkeypatch.setattr("cobra.cli.commands.compile_cmd.validar_dependencias", lambda *a, **k: None)
    monkeypatch.setattr("cobra.cli.commands.compile_cmd.obtener_ast", lambda codigo: [])
    monkeypatch.setattr("cobra.cli.commands.compile_cmd.mostrar_error", lambda msg: mensajes.append(msg))
    monkeypatch.setattr("cobra.cli.commands.compile_cmd.module_map.get_toml_map", lambda: {})

    args = SimpleNamespace(archivo=str(archivo), tipo="fantasia", backend=None, tipos=None)
    rc = CompileCommand().run(args)

    assert rc == 1
    assert any("Transpilador no soportado" in m for m in mensajes)


@pytest.mark.timeout(5)
def test_dependencia_faltante(monkeypatch, tmp_path):
    archivo = tmp_path / "code.co"
    archivo.write_text("x = 1")
    mensajes = []

    def fake_validar(lang, mod_info):
        raise FileNotFoundError("dep faltante")

    monkeypatch.setattr("cobra.cli.commands.compile_cmd.validar_dependencias", fake_validar)
    monkeypatch.setattr("cobra.cli.commands.compile_cmd.obtener_ast", lambda codigo: [])
    monkeypatch.setattr("cobra.cli.commands.compile_cmd.mostrar_error", lambda msg: mensajes.append(msg))
    monkeypatch.setattr("cobra.cli.commands.compile_cmd.module_map.get_toml_map", lambda: {})

    args = SimpleNamespace(archivo=str(archivo), tipo="python", backend=None, tipos=None)
    rc = CompileCommand().run(args)

    assert rc == 1
    assert any("Error de dependencias" in m for m in mensajes)


@pytest.mark.timeout(5)
def test_archivo_invalido(monkeypatch, tmp_path):
    archivo = tmp_path / "no_existe.co"
    mensajes = []

    monkeypatch.setattr("cobra.cli.commands.compile_cmd.validar_dependencias", lambda *a, **k: None)
    monkeypatch.setattr("cobra.cli.commands.compile_cmd.obtener_ast", lambda codigo: [])
    monkeypatch.setattr("cobra.cli.commands.compile_cmd.mostrar_error", lambda msg: mensajes.append(msg))

    args = SimpleNamespace(archivo=str(archivo), tipo="python", backend=None, tipos=None)
    rc = CompileCommand().run(args)

    assert rc == 1
    assert any("no es un archivo válido" in m for m in mensajes)


@pytest.mark.timeout(5)
def test_exceso_tipos(monkeypatch, tmp_path):
    archivo = tmp_path / "code.co"
    archivo.write_text("x = 1")
    mensajes = []

    monkeypatch.setattr("cobra.cli.commands.compile_cmd.validar_dependencias", lambda *a, **k: None)
    monkeypatch.setattr("cobra.cli.commands.compile_cmd.obtener_ast", lambda codigo: [])
    monkeypatch.setattr("cobra.cli.commands.compile_cmd.mostrar_error", lambda msg: mensajes.append(msg))
    monkeypatch.setattr("cobra.cli.commands.compile_cmd.module_map.get_toml_map", lambda: {})

    many_langs = "python,js,c,cpp,go,java,cobol,fortran,pascal,php,rust"
    args = SimpleNamespace(archivo=str(archivo), tipo="python", backend=None, tipos=many_langs)
    rc = CompileCommand().run(args)

    assert rc == 1
    assert any("Demasiados lenguajes" in m for m in mensajes)
