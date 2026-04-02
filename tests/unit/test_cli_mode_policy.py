from types import SimpleNamespace

from importlib import import_module
import argparse
import types

compile_module = import_module("cobra.cli.commands.compile_cmd")
execute_module = import_module("cobra.cli.commands.execute_cmd")
cli_module = import_module("cobra.cli.cli")
CompileCommand = compile_module.CompileCommand
ExecuteCommand = execute_module.ExecuteCommand
CliApplication = cli_module.CliApplication


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


def test_menu_modo_cobra_bloquea_transpilacion(monkeypatch):
    app = CliApplication()
    app.command_registry = types.SimpleNamespace(commands={}, get_default_command=lambda: None)
    mensajes_error = []
    mensajes_info = []

    monkeypatch.setattr("cobra.cli.cli.sys.stdin", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr("cobra.cli.cli.messages.mostrar_error", lambda msg: mensajes_error.append(msg))
    monkeypatch.setattr("cobra.cli.cli.messages.mostrar_info", lambda msg: mensajes_info.append(msg))
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(AssertionError("no debe pedir input")))

    rc = app.execute_command(argparse.Namespace(cmd="menu", modo="cobra", lang="es"))

    assert rc == 1
    assert any("transpilación del menú está bloqueada por --modo cobra" in m for m in mensajes_error)
    assert any("no está permitido en modo 'cobra'" in m for m in mensajes_info)


def test_menu_modo_transpilar_no_ejecuta_comando_ejecutar(monkeypatch):
    app = CliApplication()
    app.command_registry = types.SimpleNamespace(commands={}, get_default_command=lambda: None)
    llamadas_ejecutar = {"count": 0}
    mensajes_info = []

    monkeypatch.setattr("cobra.cli.cli.sys.stdin", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr("cobra.cli.cli.messages.mostrar_info", lambda msg: mensajes_info.append(msg))
    monkeypatch.setattr("cobra.cli.cli.messages.mostrar_error", lambda msg: (_ for _ in ()).throw(AssertionError(msg)))
    monkeypatch.setattr("builtins.input", lambda _: "n")
    monkeypatch.setattr(
        "cobra.cli.commands.execute_cmd.ExecuteCommand.run",
        lambda *_: llamadas_ejecutar.__setitem__("count", llamadas_ejecutar["count"] + 1),
    )

    rc = app.execute_command(argparse.Namespace(cmd="menu", modo="transpilar", lang="es"))

    assert rc == 0
    assert llamadas_ejecutar["count"] == 0
    assert any("opción 'ejecutar' está deshabilitada" in m for m in mensajes_info)
