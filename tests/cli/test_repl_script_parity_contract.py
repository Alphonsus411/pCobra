from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest
from unittest.mock import patch

from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.execution_pipeline import (
    PipelineInput,
    ejecutar_pipeline_explicito,
    resolver_interpretador_cls,
)
from pcobra.cobra.core.runtime import InterpretadorCobra


def _valor_en_contextos(interpretador: InterpretadorCobra, nombre: str):
    for contexto in reversed(interpretador.contextos):
        try:
            return contexto.get(nombre)
        except NameError:
            continue
    raise NameError(f"Variable no declarada: {nombre}")


def _ejecutar_por_ruta_script(
    codigo: str,
    variables_estado: tuple[str, ...],
    *,
    prelude: str = "",
) -> dict[str, object]:
    interpretador_cls = resolver_interpretador_cls(
        module_name="pcobra.cobra.cli.services.run_service",
        default_cls=InterpretadorCobra,
    )
    out_script, err_script = StringIO(), StringIO()
    with redirect_stdout(out_script), redirect_stderr(err_script):
        with patch.object(
            InterpretadorCobra,
            "_asegurar_no_autorreferencia_asignacion",
            return_value=None,
        ):
            interpretador = None
            if prelude:
                setup_preludio, _ = ejecutar_pipeline_explicito(
                    PipelineInput(
                        codigo=prelude,
                        interpretador_cls=interpretador_cls,
                        safe_mode=False,
                        extra_validators=None,
                    )
                )
                interpretador = setup_preludio.interpretador
            setup, _resultado = ejecutar_pipeline_explicito(
                PipelineInput(
                    codigo=codigo,
                    interpretador_cls=interpretador_cls,
                    safe_mode=False,
                    extra_validators=None,
                    interpretador=interpretador,
                )
            )

    estado = {
        nombre: _valor_en_contextos(setup.interpretador, nombre)
        for nombre in variables_estado
    }
    return {
        "stdout": out_script.getvalue(),
        "stderr": err_script.getvalue(),
        "estado": estado,
    }


def _ejecutar_por_ruta_repl(
    codigo: str,
    variables_estado: tuple[str, ...],
    *,
    prelude: str = "",
) -> dict[str, object]:
    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None

    out_repl, err_repl = StringIO(), StringIO()
    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        with patch.object(
            InterpretadorCobra,
            "_asegurar_no_autorreferencia_asignacion",
            return_value=None,
        ):
            if prelude:
                repl.ejecutar_codigo(prelude)
            repl.ejecutar_codigo(codigo)

    estado = {
        nombre: _valor_en_contextos(repl.interpretador, nombre)
        for nombre in variables_estado
    }
    return {
        "stdout": out_repl.getvalue(),
        "stderr": err_repl.getvalue(),
        "estado": estado,
    }


@pytest.mark.integration
def test_paridad_script_vs_repl_mientras_asignaciones_y_retorno_observable() -> None:
    codigo = (
        "func calcular():\n"
        "    retorno contador\n"
        "fin\n"
        "var resultado = calcular()"
    )
    prelude = (
        "var contador = 1\n"
        "mientras verdadero:\n"
        "    contador = 4\n"
        "    romper\n"
        "fin"
    )
    variables = ("contador", "resultado")

    resultado_script = _ejecutar_por_ruta_script(codigo, variables, prelude=prelude)
    resultado_repl = _ejecutar_por_ruta_repl(codigo, variables, prelude=prelude)

    assert resultado_script["stderr"] == resultado_repl["stderr"] == ""
    assert resultado_script["stdout"] == resultado_repl["stdout"]
    assert resultado_script["estado"] == resultado_repl["estado"]
    assert resultado_script["estado"] == {"contador": 1, "resultado": 1}


@pytest.mark.integration
def test_paridad_error_identificador_no_declarado_en_script_y_repl() -> None:
    codigo_erroneo = "imprimir(no_declarado)"

    with pytest.raises(Exception) as err_script:  # noqa: BLE001 - contrato de paridad
        _ejecutar_por_ruta_script(codigo_erroneo, ("no_declarado",))

    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None

    with pytest.raises(Exception) as err_repl:  # noqa: BLE001 - contrato de paridad
        repl.ejecutar_codigo(codigo_erroneo)

    assert type(err_script.value) is type(err_repl.value)
    assert str(err_script.value) == str(err_repl.value)
