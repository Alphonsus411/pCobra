from argparse import Namespace
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from pcobra.cobra.cli.commands_v2.run_cmd import RunCommandV2
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.execution_pipeline import (
    PipelineInput,
    ejecutar_pipeline_explicito,
    resolver_interpretador_cls,
)
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
    monkeypatch.setattr("pcobra.cobra.cli.services.run_service.limitar_cpu_segundos", lambda *_: None)
    codigo = (
        "mientras verdadero:\n"
        "    var total = 7\n"
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
            "    var dato = 2\n"
            "    romper\n"
            "fin"
        )
        repl.ejecutar_codigo("var dato = 3")
        repl.ejecutar_codigo("imprimir(dato)")

    assert err_repl.getvalue() == ""
    assert out_repl.getvalue().strip().endswith("3")
    assert repl.interpretador.contextos[-1].get("dato") == 3


@pytest.mark.integration
def test_anidacion_condicional_bucle_equivale_en_salida_y_estado(tmp_path, monkeypatch):
    monkeypatch.setattr("pcobra.cobra.cli.services.run_service.limitar_cpu_segundos", lambda *_: None)
    codigo = (
        "si verdadero:\n"
        "    mientras verdadero:\n"
        "        var total = 5\n"
        "        romper\n"
        "    fin\n"
        "fin"
    )
    archivo = tmp_path / "anidado.co"
    archivo.write_text(codigo, encoding="utf-8")

    out_run, err_run = StringIO(), StringIO()
    with redirect_stdout(out_run), redirect_stderr(err_run):
        rc_run = RunCommandV2().run(_run_args(str(archivo)))

    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    out_repl, err_repl = StringIO(), StringIO()
    with pytest.raises(Exception) as err_repl_exc:  # noqa: BLE001 - contrato integración
        with redirect_stdout(out_repl), redirect_stderr(err_repl):
            repl.ejecutar_codigo(codigo)

    with pytest.raises(Exception) as err_script_exc:  # noqa: BLE001 - contrato integración
        ejecutar_pipeline_explicito(
            PipelineInput(
                codigo=codigo,
                interpretador_cls=resolver_interpretador_cls(
                    module_name="pcobra.cobra.cli.services.run_service",
                    default_cls=InterpretadorCobra,
                ),
                safe_mode=False,
                extra_validators=None,
            )
        )

    assert rc_run == 1
    assert type(err_script_exc.value) is type(err_repl_exc.value)
    assert str(err_script_exc.value) == str(err_repl_exc.value)


@pytest.mark.integration
@pytest.mark.parametrize(
    "codigo_erroneo",
    [
        "no_definida = 1",
        "var x = 10 / 0",
    ],
)
def test_error_semantico_y_runtime_equivalen_en_tipo_y_mensaje(codigo_erroneo):
    interpretador_cls = resolver_interpretador_cls(
        module_name="pcobra.cobra.cli.services.run_service",
        default_cls=InterpretadorCobra,
    )

    with pytest.raises(Exception) as err_script:  # noqa: BLE001 - contrato integración
        ejecutar_pipeline_explicito(
            PipelineInput(
                codigo=codigo_erroneo,
                interpretador_cls=interpretador_cls,
                safe_mode=False,
                extra_validators=None,
            )
        )

    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    with pytest.raises(Exception) as err_repl:  # noqa: BLE001 - contrato integración
        repl.ejecutar_codigo(codigo_erroneo)

    assert type(err_script.value) is type(err_repl.value)
    assert str(err_script.value) == str(err_repl.value)
