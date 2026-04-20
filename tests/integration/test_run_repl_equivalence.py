from argparse import Namespace
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from pcobra.cobra.cli.commands_v2.run_cmd import RunCommandV2
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.core.runtime import InterpretadorCobra


def _run_args(file_path: str) -> Namespace:
    return Namespace(
        file=file_path,
        debug=False,
        sandbox=False,
        container=None,
        formatear=False,
        modo="mixto",
    )


@pytest.mark.integration
def test_misma_secuencia_semantica_equivale_entre_run_y_repl(tmp_path, monkeypatch):
    monkeypatch.setattr("pcobra.cobra.cli.commands.execute_cmd.limitar_cpu_segundos", lambda *_: None)
    codigo = (
        "mientras verdadero:\n"
        "    total = 7\n"
        "    romper\n"
        "fin"
    )
    archivo = tmp_path / "programa.co"
    archivo.write_text(codigo, encoding="utf-8")

    out_run, err_run = StringIO(), StringIO()
    with redirect_stdout(out_run), redirect_stderr(err_run):
        rc_run = RunCommandV2().run(_run_args(str(archivo)))

    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    out_repl, err_repl = StringIO(), StringIO()
    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        repl.ejecutar_codigo(codigo)

    assert rc_run == 0
    assert err_run.getvalue() == err_repl.getvalue() == ""
    assert out_run.getvalue() == out_repl.getvalue()


@pytest.mark.integration
def test_mutacion_en_mientras_y_lectura_posterior_persisten_en_repl():
    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    out_repl, err_repl = StringIO(), StringIO()
    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        repl.ejecutar_codigo(
            "mientras verdadero:\n"
            "    dato = 2\n"
            "    romper\n"
            "fin"
        )
        repl.ejecutar_codigo("imprimir(dato)")

    assert err_repl.getvalue() == ""
    assert out_repl.getvalue().strip().endswith("2")
    assert repl.interpretador.contextos[-1].get("dato") == 2
