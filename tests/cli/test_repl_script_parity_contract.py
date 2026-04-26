from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from types import SimpleNamespace
import re

import pytest
from unittest.mock import patch

from pcobra.cobra.cli.commands_v2 import repl_cmd as repl_v2_module
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.execution_pipeline import (
    PipelineInput,
    ejecutar_pipeline_explicito,
    resolver_interpretador_cls,
)
from pcobra.cobra.core import ParserError, TipoToken
from pcobra.cobra.core.runtime import InterpretadorCobra


def _valor_en_contextos(interpretador: InterpretadorCobra, nombre: str):
    for contexto in reversed(interpretador.contextos):
        try:
            return contexto.get(nombre)
        except NameError:
            continue
    raise NameError(f"Variable no declarada: {nombre}")


def _normalizar_stdout_paridad(salida: str) -> str:
    """Filtra eco implícito del REPL para comparar con la ruta script."""

    lineas = [linea.strip() for linea in salida.splitlines() if linea.strip()]
    return "\n".join(linea for linea in lineas if not linea.isdigit())


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


def _ejecutar_snippets_secuenciales_script(
    snippets: list[str], *, variables_estado: tuple[str, ...]
) -> dict[str, object]:
    interpretador_cls = resolver_interpretador_cls(
        module_name="pcobra.cobra.cli.services.run_service",
        default_cls=InterpretadorCobra,
    )
    out_script, err_script = StringIO(), StringIO()
    excepcion: Exception | None = None
    setup = None
    with redirect_stdout(out_script), redirect_stderr(err_script):
        with patch.object(
            InterpretadorCobra,
            "_asegurar_no_autorreferencia_asignacion",
            return_value=None,
        ):
            try:
                interpretador = None
                for snippet in snippets:
                    setup, resultado_pipeline = ejecutar_pipeline_explicito(
                        PipelineInput(
                            codigo=snippet,
                            interpretador_cls=interpretador_cls,
                            safe_mode=False,
                            extra_validators=None,
                            interpretador=interpretador,
                        )
                    )
                    interpretador = setup.interpretador
            except Exception as err:  # noqa: BLE001 - contrato de paridad
                excepcion = err

    estado = {}
    if setup is not None:
        for nombre in variables_estado:
            try:
                estado[nombre] = _valor_en_contextos(setup.interpretador, nombre)
            except NameError:
                continue
    return {
        "stdout": out_script.getvalue(),
        "stderr": err_script.getvalue(),
        "estado": estado,
        "error": excepcion,
    }


def _ejecutar_snippets_secuenciales_repl(
    snippets: list[str], *, variables_estado: tuple[str, ...]
) -> dict[str, object]:
    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    out_repl, err_repl = StringIO(), StringIO()
    excepcion: Exception | None = None
    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        with patch.object(
            InterpretadorCobra,
            "_asegurar_no_autorreferencia_asignacion",
            return_value=None,
        ):
            try:
                for snippet in snippets:
                    repl.ejecutar_codigo(snippet)
            except Exception as err:  # noqa: BLE001 - contrato de paridad
                excepcion = err

    estado = {}
    if excepcion is None:
        for nombre in variables_estado:
            try:
                estado[nombre] = _valor_en_contextos(repl.interpretador, nombre)
            except NameError:
                continue
    return {
        "stdout": out_repl.getvalue(),
        "stderr": err_repl.getvalue(),
        "estado": estado,
        "error": excepcion,
    }


def _ejecutar_repl_v2_con_entradas(entradas: list[str]) -> dict[str, object]:
    repl = repl_v2_module.ReplCommandV2()
    args = SimpleNamespace(seguro=False, extra_validators=None, sandbox=False, sandbox_docker=None)
    out_repl, err_repl = StringIO(), StringIO()
    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        with patch.object(
            InterpretadorCobra,
            "_asegurar_no_autorreferencia_asignacion",
            return_value=None,
        ):
            with patch("builtins.input", side_effect=entradas + ["salir"]):
                repl.run(args)

    return {
        "stdout": out_repl.getvalue(),
        "stderr": err_repl.getvalue(),
        "interpretador": repl._interpretador_persistente,
    }


def _lineas_stdout_repl_v2(resultado: dict[str, object]) -> list[str]:
    salida = str(resultado["stdout"])
    salida_sin_ansi = re.sub(r"\x1b\[[0-9;]*m", "", salida)
    return [
        linea.strip()
        for linea in salida_sin_ansi.splitlines()
        if linea.strip() and "Saliendo..." not in linea
    ]


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


@pytest.mark.integration
def test_paridad_script_vs_repl_con_snippets_secuenciales_y_estado_final() -> None:
    snippets = [
        "var acumulado = 1",
        "var salida = 15",
        "var eco = salida",
    ]
    variables = ("acumulado",)

    resultado_script = _ejecutar_snippets_secuenciales_script(
        snippets, variables_estado=variables
    )
    resultado_repl = _ejecutar_snippets_secuenciales_repl(
        snippets, variables_estado=variables
    )

    assert resultado_repl["error"] is None
    assert resultado_script["error"] is None
    assert resultado_script["stderr"] == resultado_repl["stderr"] == ""
    assert _normalizar_stdout_paridad(resultado_script["stdout"]) == _normalizar_stdout_paridad(
        resultado_repl["stdout"]
    ) == ""
    assert resultado_script["estado"] == resultado_repl["estado"] == {
        "acumulado": 1,
    }


@pytest.mark.integration
def test_paridad_script_vs_repl_con_error_en_snippet_secuencial() -> None:
    snippets = [
        "var base = 7",
        "var siguiente = base + 1",
        "imprimir(no_existe_en_ambas_rutas)",
    ]

    resultado_script = _ejecutar_snippets_secuenciales_script(snippets, variables_estado=("base",))
    resultado_repl = _ejecutar_snippets_secuenciales_repl(snippets, variables_estado=("base",))

    assert resultado_script["error"] is not None
    assert resultado_repl["error"] is not None
    assert type(resultado_script["error"]) is type(resultado_repl["error"])
    assert str(resultado_script["error"]) == str(resultado_repl["error"])


@pytest.mark.integration
def test_paridad_script_vs_repl_bloque_anidado_mientras_con_si_y_fin() -> None:
    snippets = [
        "var acumulado = 0",
        (
            "mientras verdadero:\n"
            "    si acumulado == 0:\n"
            "        imprimir(acumulado)\n"
            "    fin\n"
            "    romper\n"
            "fin"
        ),
    ]
    variables = ("acumulado",)

    codigo_script = "\n".join(snippets)
    resultado_script = _ejecutar_por_ruta_script(codigo_script, variables)
    resultado_repl = _ejecutar_snippets_secuenciales_repl(
        snippets, variables_estado=variables
    )

    assert resultado_script["stderr"] == resultado_repl["stderr"] == ""
    assert resultado_repl["error"] is None
    assert _normalizar_stdout_paridad(resultado_script["stdout"]) == _normalizar_stdout_paridad(
        resultado_repl["stdout"]
    )
    assert resultado_script["estado"] == resultado_repl["estado"] == {"acumulado": 0}


@pytest.mark.integration
def test_repl_v2_preserva_estado_entre_entradas_sin_recrear_interpretador() -> None:
    entradas = ["var base = 41", "imprimir(base)"]
    interpretadores_entrada: list[object | None] = []
    interpretador_persistente = object()

    def _spy_parsear_y_ejecutar_codigo_repl(self, codigo: str, prevalidar_fn):
        prevalidar_fn(codigo)
        interpretadores_entrada.append(self.interpretador)
        self.interpretador = interpretador_persistente

    with patch.object(
        InteractiveCommand,
        "parsear_y_ejecutar_codigo_repl",
        _spy_parsear_y_ejecutar_codigo_repl,
    ):
        _ = _ejecutar_repl_v2_con_entradas(entradas)

    assert len(interpretadores_entrada) == 2
    assert interpretadores_entrada[0] is not None
    assert interpretadores_entrada[1] is interpretador_persistente


@pytest.mark.integration
def test_repl_v2_detecta_bloque_anidado_completo_solo_por_parser() -> None:
    entradas = [
        "mientras verdadero:",
        "    si verdadero:",
        "        imprimir(7)",
        "    fin",
        "    romper",
        "fin",
    ]
    codigos_parseados: list[str] = []
    codigos_ejecutados: list[str] = []

    def _spy_parse(codigo: str):
        codigos_parseados.append(codigo)
        if codigo != "\n".join(entradas):
            err = ParserError("incompleto")
            err.esperado = [TipoToken.FIN]
            err.unexpected_eof = True
            err.tipo_token_actual = TipoToken.EOF
            raise err
        return [object()]

    def _spy_parsear_y_ejecutar_codigo_repl(_self, codigo: str, prevalidar_fn):
        prevalidar_fn(codigo)
        codigos_ejecutados.append(codigo)

    with patch.object(repl_v2_module, "prevalidar_y_parsear_codigo", _spy_parse):
        with patch.object(
            InteractiveCommand,
            "parsear_y_ejecutar_codigo_repl",
            _spy_parsear_y_ejecutar_codigo_repl,
        ):
            resultado = _ejecutar_repl_v2_con_entradas(entradas)

    assert resultado["stderr"] == ""
    assert codigos_parseados[-1] == "\n".join(entradas)
    assert codigos_ejecutados == ["\n".join(entradas)]


@pytest.mark.integration
def test_repl_v2_echo_expresiones_y_estado_persistente_en_entradas_secuenciales() -> None:
    resultado = _ejecutar_repl_v2_con_entradas([
        "var x = 5",
        "x + 10",
        "x * 2",
    ])

    lineas = _lineas_stdout_repl_v2(resultado)

    assert resultado["stderr"] == ""
    assert lineas[:2] == ["15", "10"]


@pytest.mark.integration
def test_repl_v2_reporta_error_real_en_expresion_con_variable_no_declarada() -> None:
    resultado = _ejecutar_repl_v2_con_entradas([
        "x + 10",
    ])

    assert resultado["stderr"] == ""
    assert "Variable no declarada: x" in str(resultado["stdout"])
    assert "nodo no soportado" not in str(resultado["stdout"]).lower()


@pytest.mark.integration
def test_repl_v2_no_altera_semantica_en_statements_var_imprimir_y_si_fin() -> None:
    resultado = _ejecutar_repl_v2_con_entradas([
        "var bandera = verdadero",
        "si bandera:",
        "    imprimir(10)",
        "fin",
        "imprimir(20)",
    ])

    lineas = _lineas_stdout_repl_v2(resultado)

    assert resultado["stderr"] == ""
    assert lineas == ["10", "20"]
