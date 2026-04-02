from types import SimpleNamespace

from importlib import import_module
import argparse
import types
import pytest

compile_module = import_module("cobra.cli.commands.compile_cmd")
execute_module = import_module("cobra.cli.commands.execute_cmd")
cli_module = import_module("cobra.cli.cli")
CompileCommand = compile_module.CompileCommand
ExecuteCommand = execute_module.ExecuteCommand
CliApplication = cli_module.CliApplication

verify_module = import_module("cobra.cli.commands.verify_cmd")
inverse_module = import_module("cobra.cli.commands.transpilar_inverso_cmd")
validar_sintaxis_module = import_module("cobra.cli.commands.validar_sintaxis_cmd")
qa_validar_module = import_module("cobra.cli.commands.qa_validar_cmd")
mode_policy_module = import_module("cobra.cli.mode_policy")
VerifyCommand = verify_module.VerifyCommand
TranspilarInversoCommand = inverse_module.TranspilarInversoCommand
ValidarSintaxisCommand = validar_sintaxis_module.ValidarSintaxisCommand
QaValidarCommand = qa_validar_module.QaValidarCommand


@pytest.mark.parametrize(
    "command_name",
    ["compilar", "transpilar", "verificar", "transpilar-inverso", "validar-sintaxis", "qa-validar"],
)
def test_modo_cobra_bloquea_todos_los_comandos_codegen(command_name):
    args = SimpleNamespace(modo="cobra")

    with pytest.raises(ValueError, match="no está permitido"):
        mode_policy_module.validar_politica_modo(command_name, args)


def test_modo_cobra_permite_ejecutar():
    args = SimpleNamespace(modo="cobra")

    mode_policy_module.validar_politica_modo("ejecutar", args)


def test_modo_cobra_bloquea_verificar(monkeypatch, tmp_path):
    archivo = tmp_path / "demo.co"
    archivo.write_text("imprimir(1)", encoding="utf-8")
    mensajes = []

    monkeypatch.setattr(verify_module, "mostrar_error", lambda msg: mensajes.append(msg))

    args = SimpleNamespace(archivo=str(archivo), lenguajes=["python"], modo="cobra")
    rc = VerifyCommand().run(args)

    assert rc == 1
    assert any("no está permitido" in m and "--modo" in m for m in mensajes)


def test_modo_cobra_bloquea_transpilar_inverso(monkeypatch, tmp_path):
    archivo = tmp_path / "demo.py"
    archivo.write_text("print(1)", encoding="utf-8")
    mensajes = []

    monkeypatch.setattr(inverse_module, "mostrar_error", lambda msg: mensajes.append(msg))

    args = SimpleNamespace(archivo=str(archivo), origen="python", destino="python", modo="cobra")
    rc = TranspilarInversoCommand().run(args)

    assert rc == 1
    assert any("no está permitido" in m and "--modo" in m for m in mensajes)


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


def test_menu_modo_cobra_muestra_solo_ejecutar(monkeypatch):
    app = CliApplication()
    ejecutar_cmd = types.SimpleNamespace(run=lambda args: 0)
    app.command_registry = types.SimpleNamespace(
        commands={"ejecutar": ejecutar_cmd},
        get_default_command=lambda: None,
    )
    mensajes_info = []

    monkeypatch.setattr("cobra.cli.cli.sys.stdin", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr("cobra.cli.cli.messages.mostrar_info", lambda msg: mensajes_info.append(msg))
    monkeypatch.setattr("builtins.input", lambda _: "archivo.co")

    rc = app.execute_command(argparse.Namespace(cmd="menu", modo="cobra", lang="es"))

    assert rc == 0
    assert any("menú limitado a 'ejecutar'" in m for m in mensajes_info)


def test_menu_modo_transpilar_muestra_solo_transpilar(monkeypatch):
    app = CliApplication()
    compilar_cmd = types.SimpleNamespace(run=lambda args: 0)
    inv_cmd = types.SimpleNamespace(run=lambda args: 0)
    app.command_registry = types.SimpleNamespace(
        commands={"compilar": compilar_cmd, "transpilar-inverso": inv_cmd},
        get_default_command=lambda: None,
    )
    llamadas_ejecutar = {"count": 0}
    mensajes_info = []

    monkeypatch.setattr("cobra.cli.cli.sys.stdin", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr("cobra.cli.cli.messages.mostrar_info", lambda msg: mensajes_info.append(msg))
    monkeypatch.setattr("cobra.cli.cli.messages.mostrar_error", lambda msg: (_ for _ in ()).throw(AssertionError(msg)))
    respuestas = iter(["s", "archivo.co", "python"])
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))
    monkeypatch.setattr(
        "cobra.cli.commands.execute_cmd.ExecuteCommand.run",
        lambda *_: llamadas_ejecutar.__setitem__("count", llamadas_ejecutar["count"] + 1),
    )

    rc = app.execute_command(argparse.Namespace(cmd="menu", modo="transpilar", lang="es"))

    assert rc == 0
    assert llamadas_ejecutar["count"] == 0
    assert any("menú limitado a 'transpilar'" in m for m in mensajes_info)


def test_compile_command_declara_alias_transpilar():
    assert "transpilar" in CompileCommand.aliases


def test_capabilities_declaradas_en_comandos_principales():
    assert ExecuteCommand.capability == "execute"
    assert CompileCommand.capability == "codegen"
    assert VerifyCommand.capability == "codegen"
    assert TranspilarInversoCommand.capability == "codegen"


def test_flag_global_solo_cobra_equivale_a_modo_cobra():
    app = CliApplication()
    app.initialize()

    args = app._parse_arguments(["--solo-cobra", "menu"])

    assert args.solo_cobra is True
    assert args.modo == "cobra"


def test_help_global_refuerza_solo_programar_interpretar_sin_codegen():
    app = CliApplication()
    app.initialize()

    help_text = app.parser.format_help()

    assert "--solo-cobra" in help_text
    assert "solo programar/interpretar Cobra sin codegen" in help_text


@pytest.mark.parametrize(
    ("module", "command", "args"),
    [
        (compile_module, CompileCommand(), SimpleNamespace(archivo="demo.co", tipo="python", backend=None, tipos=None, modo="cobra")),
        (verify_module, VerifyCommand(), SimpleNamespace(archivo="demo.co", lenguajes=["python"], modo="cobra")),
        (inverse_module, TranspilarInversoCommand(), SimpleNamespace(archivo="demo.py", origen="python", destino="javascript", modo="cobra")),
        (validar_sintaxis_module, ValidarSintaxisCommand(), SimpleNamespace(modo="cobra", perfil="transpiladores", strict=False, solo_cobra=False, targets="", report_json=None)),
        (qa_validar_module, QaValidarCommand(), SimpleNamespace(modo="cobra", scope="syntax", strict=False, archivo="demo.co", targets="", report_json=None)),
    ],
)
def test_comandos_codegen_bloqueados_muestran_mensaje_homogeneo(module, command, args, monkeypatch):
    mensajes = []
    monkeypatch.setattr(module, "mostrar_error", lambda msg: mensajes.append(msg))

    rc = command.run(args)

    assert rc == 1
    assert any("Acción sugerida: cambia a --modo mixto o --modo transpilar" in m for m in mensajes)
