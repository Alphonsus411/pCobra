"""Regresiones de acoplamiento para REPL interactivo.

Nota changelog interno: se corrige la ejecución interactiva para que la ruta
normal no dependa de temporales internos del backend.
"""

from types import ModuleType
import re
import sys

# Dependencias opcionales simuladas para aislar estas pruebas unitarias.
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

from unittest.mock import patch
from io import StringIO
from types import SimpleNamespace

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


def test_parsear_y_ejecutar_repl_normal_no_usa_pipeline_explicito() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())

    with patch(
        "pcobra.cobra.cli.execution_pipeline.ejecutar_pipeline_explicito",
        side_effect=AssertionError("No debe usarse pipeline explícito en ruta normal"),
    ):
        cmd.parsear_y_ejecutar_codigo_repl("var x = 1")
        cmd.parsear_y_ejecutar_codigo_repl("x")


def test_repl_sandbox_setup_si_usa_pipeline_explicito() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())

    setup_stub = ModuleType("setup")
    setup_stub.interpretador = cmd.interpretador
    setup_stub.safe_mode = False
    setup_stub.validadores_extra = None

    with patch(
        "pcobra.cobra.cli.execution_pipeline.ejecutar_pipeline_explicito",
        return_value=(setup_stub, None),
    ) as pipeline_mock, patch(
        "cobra.cli.commands.interactive_cmd.ejecutar_en_sandbox",
        return_value="",
    ):
        cmd._ejecutar_en_sandbox("var x = 1")

    pipeline_mock.assert_called_once()


def test_run_repl_normal_incremental_no_invoca_pipeline_batch_y_comparte_entorno() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())
    entradas = ["var x = 10", "var y = x * 2", "si verdadero:", "var z = y", "fin", "z", "salir"]

    with patch("cobra.cli.commands.interactive_cmd.validar_dependencias"), patch(
        "prompt_toolkit.PromptSession.prompt", side_effect=entradas
    ), patch(
        "cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada", return_value=True
    ), patch(
        "pcobra.cobra.cli.execution_pipeline.ejecutar_pipeline_explicito",
        side_effect=AssertionError("No debe usarse pipeline explícito en flujo REPL normal"),
    ), patch("sys.stdout", new_callable=StringIO) as salida:
        ret = cmd.run(_args())

    evidencia = salida.getvalue()
    assert ret == 0
    assert "20" in evidencia
    assert "Variable no declarada: _cse0" not in evidencia
    assert re.search(r"Variable no declarada:\s*_cse\d+", evidencia) is None
