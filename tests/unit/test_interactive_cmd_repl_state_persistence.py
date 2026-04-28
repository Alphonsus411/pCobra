from io import StringIO
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
import sys
import pytest

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


def test_repl_normal_persiste_estado_entre_snippets_y_no_filtra_cse() -> None:
    entradas = ["var x = 21", "var y = x * 2", "y", "salir"]

    with patch("cobra.cli.commands.interactive_cmd.validar_dependencias"), \
         patch("prompt_toolkit.PromptSession.prompt", side_effect=entradas), \
         patch("cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada", return_value=True), \
         patch("sys.stdout", new_callable=StringIO) as salida:
        cmd = InteractiveCommand(InterpretadorCobra())
        ret = cmd.run(_args())

    assert ret == 0

    evidencia = salida.getvalue()
    assert "42" in evidencia
    assert "Variable no declarada" not in evidencia
    assert "_cse" not in evidencia


def test_repl_imprime_resultado_en_expresion_simple() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())

    with patch("sys.stdout", new_callable=StringIO) as salida:
        cmd.ejecutar_codigo("1 + 2")

    assert salida.getvalue() == "3\n"


def test_repl_asignacion_no_hace_echo_extra_y_lectura_posterior_si_imprime() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())

    with patch("sys.stdout", new_callable=StringIO) as salida:
        cmd.ejecutar_codigo("var a = 5")
        cmd.ejecutar_codigo("a")

    assert salida.getvalue() == "5\n"


def test_repl_condicional_con_mutacion_estado_no_hace_echo_automatico() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())

    with patch("sys.stdout", new_callable=StringIO) as salida:
        cmd.ejecutar_codigo("var total = 0")
        cmd.ejecutar_codigo("si verdadero:\n    total = 7\nfin")
        cmd.ejecutar_codigo("total")

    assert salida.getvalue() == "7\n"


def test_fallback_imprimir_top_level_aplica_solo_en_expresiones() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())
    llamadas: list[str] = []
    error = ValueError(
        "Nodo no soportado: <class 'pcobra.core.ast_nodes.NodoOperacionBinaria'>"
    )

    def _fake_ejecutar(codigo: str, validador=None):
        del validador
        llamadas.append(codigo)
        if codigo == "1 + 2":
            raise error
        if codigo == "imprimir(1 + 2)":
            return ([object()], None)
        raise AssertionError(f"Código inesperado en fallback: {codigo}")

    with patch.object(cmd, "_ejecutar_ast_en_repl", side_effect=_fake_ejecutar), patch.object(
        cmd,
        "_debe_intentar_fallback_expresion_top_level",
        side_effect=lambda codigo, _err: codigo == "1 + 2",
    ), patch.object(cmd, "_imprimir_resultado_repl"):
        cmd.ejecutar_codigo("1 + 2")

    assert llamadas == ["1 + 2", "imprimir(1 + 2)"]


def test_fallback_no_modifica_statements_normales() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())
    llamadas: list[str] = []

    def _fake_ejecutar(codigo: str, validador=None):
        del validador
        llamadas.append(codigo)
        raise ValueError("Nodo no soportado: <class 'pcobra.core.ast_nodes.NodoAsignacion'>")

    with patch.object(cmd, "_ejecutar_ast_en_repl", side_effect=_fake_ejecutar), patch.object(
        cmd,
        "_debe_intentar_fallback_expresion_top_level",
        return_value=False,
    ), patch.object(cmd, "_imprimir_resultado_repl"):
        with pytest.raises(ValueError):
            cmd.ejecutar_codigo("var a = 5")

    assert llamadas == ["var a = 5"]
