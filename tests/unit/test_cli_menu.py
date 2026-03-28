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
    responses = iter(["n"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))

    def fail_run(self, args):
        raise AssertionError("should not run")

    monkeypatch.setattr("cobra.cli.commands.compile_cmd.CompileCommand.run", fail_run)
    monkeypatch.setattr("cobra.cli.commands.transpilar_inverso_cmd.TranspilarInversoCommand.run", fail_run)

    assert main(["menu"]) == 0


def test_menu_compile(monkeypatch):
    _set_tty(monkeypatch, True)
    inputs = iter(["s", "s", "archivo.cobra", "python"])
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
    inputs = iter(["s", "n", "archivo.py", "python", "javascript"])
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


def test_menu_no_tty_aborta_con_error(monkeypatch):
    _set_tty(monkeypatch, False)
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(AssertionError("no debe leer input")))
    assert main(["menu"]) == 1


def test_menu_eof_inmediato_devuelve_cancelacion(monkeypatch):
    _set_tty(monkeypatch, True)
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(EOFError()))
    assert main(["menu"]) == 0


def test_menu_keyboardinterrupt_devuelve_cancelacion(monkeypatch):
    _set_tty(monkeypatch, True)
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(KeyboardInterrupt()))
    assert main(["menu"]) == 0
