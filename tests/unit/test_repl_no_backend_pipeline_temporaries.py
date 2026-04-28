from io import StringIO
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
import sys

# Módulos opcionales simulados para evitar dependencias externas en pruebas unitarias.
fake_rp = ModuleType("RestrictedPython")
fake_rp.compile_restricted = lambda *a, **k: None
fake_rp.safe_builtins = {}
sys.modules.setdefault("RestrictedPython", fake_rp)

_eval_mod = ModuleType("Eval")
_eval_mod.default_guarded_getitem = lambda seq, key: seq[key]
sys.modules.setdefault("RestrictedPython.Eval", _eval_mod)

_guards_mod = ModuleType("Guards")
_guards_mod.guarded_iter_unpack_sequence = lambda *a, **k: iter([])
_guards_mod.guarded_unpack_sequence = lambda *a, **k: []
sys.modules.setdefault("RestrictedPython.Guards", _guards_mod)

_pc_mod = ModuleType("PrintCollector")
_pc_mod.PrintCollector = list
sys.modules.setdefault("RestrictedPython.PrintCollector", _pc_mod)

_yaml_mod = ModuleType("yaml")
_yaml_mod.safe_load = lambda *a, **k: {}
sys.modules.setdefault("yaml", _yaml_mod)

_tsl_mod = ModuleType("tree_sitter_languages")
_tsl_mod.get_parser = lambda *a, **k: None
sys.modules.setdefault("tree_sitter_languages", _tsl_mod)

_jsonschema_mod = ModuleType("jsonschema")
_jsonschema_mod.validate = lambda *a, **k: None
_jsonschema_mod.ValidationError = Exception
sys.modules.setdefault("jsonschema", _jsonschema_mod)

from cobra.cli.commands.interactive_cmd import InteractiveCommand
from core.interpreter import InterpretadorCobra


def _args() -> SimpleNamespace:
    return SimpleNamespace(
        seguro=False,
        extra_validators=None,
        sandbox=False,
        sandbox_docker=None,
        ignore_memory_limit=True,
        debug=False,
    )


def test_repl_incremental_var_var_evalua_resultado_sin_error_temporal_cse() -> None:
    entradas = ["var x = 10", "var y = x * 2", "y", "salir"]

    with patch("cobra.cli.commands.interactive_cmd.validar_dependencias"), \
         patch("prompt_toolkit.PromptSession.prompt", side_effect=entradas), \
         patch("cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada", return_value=True), \
         patch("sys.stdout", new_callable=StringIO) as salida:
        cmd = InteractiveCommand(InterpretadorCobra())
        ret = cmd.run(_args())

    evidencia = salida.getvalue()

    assert ret == 0
    assert "20" in evidencia
    assert "Variable no declarada: _cse0" not in evidencia
    assert "Variable no declarada: _cse" not in evidencia


def test_repl_incremental_con_bloque_si_comparte_entorno_sin_error_temporal_cse() -> None:
    entradas = [
        "var x = 10",
        "si verdadero:",
        "var y = x * 2",
        "fin",
        "y",
        "salir",
    ]

    with patch("cobra.cli.commands.interactive_cmd.validar_dependencias"), \
         patch("prompt_toolkit.PromptSession.prompt", side_effect=entradas), \
         patch("cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada", return_value=True), \
         patch("sys.stdout", new_callable=StringIO) as salida:
        cmd = InteractiveCommand(InterpretadorCobra())
        ret = cmd.run(_args())

    evidencia = salida.getvalue()

    assert ret == 0
    assert "20" in evidencia
    assert "Variable no declarada: _cse" not in evidencia
