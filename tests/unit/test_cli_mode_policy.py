from types import SimpleNamespace

from importlib import import_module

compile_module = import_module("cobra.cli.commands.compile_cmd")
execute_module = import_module("cobra.cli.commands.execute_cmd")
CompileCommand = compile_module.CompileCommand
ExecuteCommand = execute_module.ExecuteCommand


def test_modo_cobra_bloquea_compilar(monkeypatch, tmp_path):
    archivo = tmp_path / "demo.co"
    archivo.write_text("imprimir(1)", encoding="utf-8")
    mensajes = []

    monkeypatch.setattr(compile_module, "mostrar_error", lambda msg: mensajes.append(msg))

    args = SimpleNamespace(archivo=str(archivo), tipo="python", backend=None, tipos=None, modo="cobra")
    rc = CompileCommand().run(args)

    assert rc == 1
    assert any("no está permitido" in m and "--modo" in m for m in mensajes)


def test_modo_transpilar_bloquea_ejecutar(monkeypatch, tmp_path):
    archivo = tmp_path / "demo.co"
    archivo.write_text("imprimir(1)", encoding="utf-8")
    mensajes = []

    monkeypatch.setattr(execute_module, "mostrar_error", lambda msg: mensajes.append(msg))

    args = SimpleNamespace(archivo=str(archivo), sandbox=False, contenedor=None, modo="transpilar")
    rc = ExecuteCommand().run(args)

    assert rc == 1
    assert any("no está permitido" in m and "--modo" in m for m in mensajes)


def test_modo_mixto_permite_ejecutar_y_falla_por_archivo(monkeypatch, tmp_path):
    archivo = tmp_path / "no_existe.co"
    mensajes = []

    monkeypatch.setattr(execute_module, "mostrar_error", lambda msg: mensajes.append(msg))

    args = SimpleNamespace(archivo=str(archivo), sandbox=False, contenedor=None, modo="mixto")
    rc = ExecuteCommand().run(args)

    assert rc == 1
    assert any("No se encontró el archivo" in m for m in mensajes)
    assert not any("no está permitido" in m for m in mensajes)


def test_modo_transpilar_permite_compilar_y_falla_por_archivo(monkeypatch, tmp_path):
    archivo = tmp_path / "no_existe.co"
    mensajes = []

    monkeypatch.setattr(compile_module, "mostrar_error", lambda msg: mensajes.append(msg))

    args = SimpleNamespace(archivo=str(archivo), tipo="python", backend=None, tipos=None, modo="transpilar")
    rc = CompileCommand().run(args)

    assert rc == 1
    assert any("no es un archivo válido" in m for m in mensajes)
    assert not any("no está permitido" in m for m in mensajes)
