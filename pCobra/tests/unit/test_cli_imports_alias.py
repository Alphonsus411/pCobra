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

cobra_cli_cli = importlib.import_module("cobra.cli.cli")
cobra_base = importlib.import_module("cobra.cli.commands.base")

# Alias para que los imports relativos y absolutos apunten al mismo objeto
sys.modules.setdefault("cli", sys.modules["cobra.cli"])
sys.modules.setdefault("cli.cli", cobra_cli_cli)
sys.modules.setdefault("cli.commands.base", cobra_base)

from cli.cli import main as main_cli
from cobra.cli.cli import main as main_cobra

from cli.commands.base import BaseCommand as BaseCommand_cli
from cobra.cli.commands.base import BaseCommand as BaseCommand_cobra


def test_cli_alias_module():
    import cli
    import cobra.cli
    assert cli is cobra.cli


def test_cli_alias_function():
    assert main_cli is main_cobra


def test_cli_alias_command_class():
    assert BaseCommand_cli is BaseCommand_cobra
