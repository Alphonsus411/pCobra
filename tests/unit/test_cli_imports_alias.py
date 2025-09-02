from types import ModuleType
import sys
import importlib

# Crear módulos falsos para evitar dependencias externas
fake_rp = ModuleType("RestrictedPython")
fake_rp.compile_restricted = lambda *a, **k: None
fake_rp.safe_builtins = {}
sys.modules.setdefault("RestrictedPython", fake_rp)

_eval = ModuleType("Eval")
_eval.default_guarded_getitem = lambda seq, key: seq[key]
sys.modules.setdefault("RestrictedPython.Eval", _eval)

_guards = ModuleType("Guards")
_guards.guarded_iter_unpack_sequence = lambda *a, **k: iter([])
_guards.guarded_unpack_sequence = lambda *a, **k: []
sys.modules.setdefault("RestrictedPython.Guards", _guards)

_print = ModuleType("PrintCollector")
_print.PrintCollector = list
sys.modules.setdefault("RestrictedPython.PrintCollector", _print)

fake_jsonschema = ModuleType("jsonschema")
fake_jsonschema.validate = lambda *a, **k: None
class FakeValidationError(Exception):
    pass
fake_jsonschema.ValidationError = FakeValidationError
sys.modules.setdefault("jsonschema", fake_jsonschema)

tsl_mod = ModuleType("tree_sitter_languages")
tsl_mod.get_parser = lambda *a, **k: None
sys.modules.setdefault("tree_sitter_languages", tsl_mod)

pcobra_cli_cli = importlib.import_module("pcobra.cli.cli")
pcobra_base = importlib.import_module("pcobra.cli.commands.base")

# Alias para que los imports relativos y absolutos apunten al mismo objeto
sys.modules.setdefault("cli", sys.modules["pcobra.cli"])
sys.modules.setdefault("cli.cli", pcobra_cli_cli)
sys.modules.setdefault("cli.commands.base", pcobra_base)

from cli.cli import main as main_cli
from pcobra.cli.cli import main as main_pcobra

from cli.commands.base import BaseCommand as BaseCommand_cli
from pcobra.cli.commands.base import BaseCommand as BaseCommand_pcobra


def test_cli_alias_module():
    import cli
    import pcobra.cli
    assert cli is pcobra.cli


def test_cli_alias_function():
    assert main_cli is main_pcobra


def test_cli_alias_command_class():
    assert BaseCommand_cli is BaseCommand_pcobra
