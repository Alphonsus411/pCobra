import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import cobra.macro
cobra.macro.expandir_macros = lambda nodos: nodos

import types
jk = types.ModuleType("jupyter_kernel")
class CobraKernel: ...
jk.CobraKernel = CobraKernel
sys.modules["jupyter_kernel"] = jk

from cobra.cli.commands.base import BaseCommand
import cobra.cli.utils as cli_utils
config_mod = types.ModuleType("cobra.cli.utils.config")
config_mod.load_config = lambda: {}
sys.modules["cobra.cli.utils.config"] = config_mod
cli_utils.config = config_mod

import core.interpreter as core_interpreter

class DummyInterpreter:
    def cleanup(self):
        pass

core_interpreter.InterpretadorCobra = DummyInterpreter

_STUBS = {
    "bench_cmd": "BenchCommand",
    "bench_transpilers_cmd": "BenchTranspilersCommand",
    "benchmarks_cmd": "BenchmarksCommand",
    "benchthreads_cmd": "BenchThreadsCommand",
    "cache_cmd": "CacheCommand",
    "container_cmd": "ContainerCommand",
    "crear_cmd": "CrearCommand",
    "dependencias_cmd": "DependenciasCommand",
    "docs_cmd": "DocsCommand",
    "empaquetar_cmd": "EmpaquetarCommand",
    "execute_cmd": "ExecuteCommand",
    "flet_cmd": "FletCommand",
    "init_cmd": "InitCommand",
    "jupyter_cmd": "JupyterCommand",
    "modules_cmd": "ModulesCommand",
    "package_cmd": "PaqueteCommand",
    "plugins_cmd": "PluginsCommand",
    "profile_cmd": "ProfileCommand",
    "qualia_cmd": "QualiaCommand",
    "verify_cmd": "VerifyCommand",
}


def _stub_command(name: str, class_name: str) -> None:
    module = types.ModuleType(f"cobra.cli.commands.{name}")

    class Dummy(BaseCommand):
        name = class_name.replace("Command", "").lower()

        def register_subparser(self, subparsers):
            parser = subparsers.add_parser(self.name)
            parser.set_defaults(cmd=self)
            return parser

        def run(self, args):
            return 0

    Dummy.__name__ = class_name
    setattr(module, class_name, Dummy)
    sys.modules[f"cobra.cli.commands.{name}"] = module


for mod, cls in _STUBS.items():
    _stub_command(mod, cls)

from cobra.cli.cli import main


def _set_tty(monkeypatch, is_tty: bool) -> None:
    fake_stdin = types.SimpleNamespace(isatty=lambda: is_tty)
    monkeypatch.setattr("cobra.cli.cli.sys.stdin", fake_stdin)


def test_menu_no_transpile(monkeypatch):
    _set_tty(monkeypatch, True)
    responses = iter(["1", "programa.co"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))

    def fail_run(self, args):
        raise AssertionError("should not run")

    monkeypatch.setattr("cobra.cli.commands.compile_cmd.CompileCommand.run", fail_run)
    monkeypatch.setattr("cobra.cli.commands.transpilar_inverso_cmd.TranspilarInversoCommand.run", fail_run)
    monkeypatch.setattr("cobra.cli.commands.execute_cmd.ExecuteCommand.run", lambda *_: 0)

    assert main(["menu"]) == 0


def test_menu_compile(monkeypatch):
    _set_tty(monkeypatch, True)
    inputs = iter(["2", "s", "archivo.cobra", "python"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    called = {}

    def fake_run(self, args):
        called['args'] = args
        return 0

    monkeypatch.setattr("cobra.cli.commands.compile_cmd.CompileCommand.run", fake_run)

    assert main(["menu"]) == 0
    assert called['args'].archivo == "archivo.cobra"
    assert called['args'].tipo == "python"


def test_menu_transpilar_inverso(monkeypatch):
    _set_tty(monkeypatch, True)
    inputs = iter(["2", "n", "archivo.py", "python", "javascript"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    called = {}

    def fake_run(self, args):
        called['args'] = args
        return 0

    monkeypatch.setattr("cobra.cli.commands.transpilar_inverso_cmd.TranspilarInversoCommand.run", fake_run)

    assert main(["menu"]) == 0
    assert called['args'].archivo == "archivo.py"
    assert called['args'].origen == "python"
    assert called['args'].destino == "javascript"


def test_menu_ejecutar_en_modo_mixto(monkeypatch):
    _set_tty(monkeypatch, True)
    inputs = iter(["1", "programa.co"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    called = {}

    def fake_run(self, args):
        called["args"] = args
        return 0

    monkeypatch.setattr("cobra.cli.commands.execute_cmd.ExecuteCommand.run", fake_run)

    assert main(["menu"]) == 0
    assert called["args"].archivo == "programa.co"


def test_menu_no_tty_aborta_con_error(monkeypatch):
    _set_tty(monkeypatch, False)
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(AssertionError("no debe leer input")))
    assert main(["menu"]) == 1


def test_menu_no_tty_no_intenta_leer_input_con_unicode_roto(monkeypatch):
    _set_tty(monkeypatch, False)
    called = {"input": False}

    def fake_input(_prompt: str) -> str:
        called["input"] = True
        return "áéíóú 🚀\ud83d"

    monkeypatch.setattr("builtins.input", fake_input)

    assert main(["menu"]) == 1
    assert called["input"] is False


def test_menu_eof_inmediato_devuelve_cancelacion(monkeypatch):
    _set_tty(monkeypatch, True)
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(EOFError()))
    assert main(["menu"]) == 0


def test_menu_keyboardinterrupt_devuelve_cancelacion(monkeypatch):
    _set_tty(monkeypatch, True)
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(KeyboardInterrupt()))
    assert main(["menu"]) == 0


def test_menu_compile_reintenta_hasta_destino_valido(monkeypatch):
    _set_tty(monkeypatch, True)
    inputs = iter(["2", "s", "archivo.cobra", "invalido", "python"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    called = {}

    def fake_run(self, args):
        called["args"] = args
        return 0

    monkeypatch.setattr("cobra.cli.commands.compile_cmd.CompileCommand.run", fake_run)

    assert main(["menu"]) == 0
    assert called["args"].tipo == "python"


def test_menu_compile_finaliza_si_supera_intentos_destino(monkeypatch):
    _set_tty(monkeypatch, True)
    inputs = iter(["2", "s", "archivo.cobra", "x", "y", "z"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    def fail_run(self, args):
        raise AssertionError("no debe ejecutar compilar")

    monkeypatch.setattr("cobra.cli.commands.compile_cmd.CompileCommand.run", fail_run)

    assert main(["menu"]) == 1


def test_menu_transpilar_inverso_reintenta_origen_y_destino(monkeypatch):
    _set_tty(monkeypatch, True)
    inputs = iter(["2", "n", "archivo.py", "nope", "python", "bad", "javascript"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    called = {}

    def fake_run(self, args):
        called["args"] = args
        return 0

    monkeypatch.setattr("cobra.cli.commands.transpilar_inverso_cmd.TranspilarInversoCommand.run", fake_run)

    assert main(["menu"]) == 0
    assert called["args"].origen == "python"
    assert called["args"].destino == "javascript"


def test_menu_destino_invalido_y_eof_cancela_controlado(monkeypatch):
    _set_tty(monkeypatch, True)
    inputs = iter(["2", "s", "archivo.cobra", "invalido"])

    def fake_input(_):
        try:
            return next(inputs)
        except StopIteration:
            raise EOFError()

    monkeypatch.setattr("builtins.input", fake_input)

    assert main(["menu"]) == 0


def test_menu_origen_invalido_y_keyboardinterrupt_cancela_controlado(monkeypatch):
    _set_tty(monkeypatch, True)
    inputs = iter(["2", "n", "archivo.py", "invalido"])

    def fake_input(_):
        try:
            return next(inputs)
        except StopIteration:
            raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", fake_input)

    assert main(["menu"]) == 0


def test_menu_modo_cobra_solo_pide_ruta_archivo(monkeypatch):
    _set_tty(monkeypatch, True)
    prompts: list[str] = []

    def fake_input(prompt: str):
        prompts.append(prompt)
        return "programa.co"

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr("cobra.cli.commands.execute_cmd.ExecuteCommand.run", lambda *_: 0)
    monkeypatch.setattr(
        "cobra.cli.commands.compile_cmd.CompileCommand.run",
        lambda *_: (_ for _ in ()).throw(AssertionError("no debe ejecutar compilar en modo cobra")),
    )
    monkeypatch.setattr(
        "cobra.cli.commands.transpilar_inverso_cmd.TranspilarInversoCommand.run",
        lambda *_: (_ for _ in ()).throw(AssertionError("no debe ejecutar transpilar-inverso en modo cobra")),
    )

    assert main(["--modo", "cobra", "menu"]) == 0
    assert prompts == ["Ruta al archivo Cobra: "]


def test_menu_solo_cobra_alias_no_pide_prompts_codegen(monkeypatch):
    _set_tty(monkeypatch, True)

    def fake_input(prompt: str):
        if "Transpilar" in prompt or "Lenguaje" in prompt or "origen" in prompt:
            raise AssertionError(f"prompt de codegen inesperado: {prompt}")
        return "programa.co"

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr("cobra.cli.commands.execute_cmd.ExecuteCommand.run", lambda *_: 0)

    assert main(["--solo-cobra", "menu"]) == 0
