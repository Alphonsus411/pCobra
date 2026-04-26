from argparse import Namespace
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest
from unittest.mock import patch

from pcobra.cobra.cli.commands_v2.run_cmd import RunCommandV2
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.execution_pipeline import (
    PipelineInput,
    ejecutar_pipeline_explicito,
    resolver_interpretador_cls,
)
from pcobra.cobra.cli.services.run_service import RunService
from pcobra.cobra.core.runtime import InterpretadorCobra, ValidadorBase


def _run_args(file_path: str) -> Namespace:
    return Namespace(
        file=file_path,
        debug=False,
        sandbox=False,
        container=None,
        formatear=False,
        modo="mixto",
    )


def _run_pipeline_and_repl(
    *,
    prelude: str,
    snippet: str,
    variables_estado: tuple[str, ...],
) -> tuple[dict[str, object], dict[str, object]]:
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
                setup_script, _ = ejecutar_pipeline_explicito(
                    PipelineInput(
                        codigo=prelude,
                        interpretador_cls=interpretador_cls,
                        safe_mode=False,
                        extra_validators=None,
                    )
                )
                interpretador = setup_script.interpretador
            setup_script, _ = ejecutar_pipeline_explicito(
                PipelineInput(
                    codigo=snippet,
                    interpretador_cls=interpretador_cls,
                    safe_mode=False,
                    extra_validators=None,
                    interpretador=interpretador,
                )
            )
    estado_script = {
        nombre: setup_script.interpretador.contextos[-1].get(nombre)
        for nombre in variables_estado
    }

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
            repl.ejecutar_codigo(snippet)

    estado_repl = {
        nombre: repl.interpretador.contextos[-1].get(nombre)
        for nombre in variables_estado
    }
    return (
        {
            "stdout": out_script.getvalue(),
            "stderr": err_script.getvalue(),
            "estado": estado_script,
        },
        {
            "stdout": out_repl.getvalue(),
            "stderr": err_repl.getvalue(),
            "estado": estado_repl,
        },
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
def test_persistencia_basica_var_x_e_impresion_equivale_entre_run_y_repl():
    resultado_script, resultado_repl = _run_pipeline_and_repl(
        prelude="var x = 10",
        snippet="imprimir(x)",
        variables_estado=("x",),
    )

    assert resultado_script["stderr"] == resultado_repl["stderr"] == ""
    assert resultado_script["estado"] == resultado_repl["estado"] == {"x": 10}


@pytest.mark.integration
def test_bloque_si_comparte_estado_posterior_equivale_entre_run_y_repl():
    resultado_script, resultado_repl = _run_pipeline_and_repl(
        prelude="var x = 5",
        snippet=(
            "si verdadero:\n"
            "    x = x * 2\n"
            "fin\n"
            "imprimir(x)"
        ),
        variables_estado=("x",),
    )

    assert resultado_script["stderr"] == resultado_repl["stderr"] == ""
    assert resultado_script["estado"] == resultado_repl["estado"] == {"x": 10}


@pytest.mark.integration
@pytest.mark.parametrize(
    ("expresion", "salida_esperada"),
    [
        ("x + 10", "15"),
        ("x * 2", "10"),
    ],
)
def test_repl_evalua_expresiones_con_estado_persistente(expresion: str, salida_esperada: str):
    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    out_repl, err_repl = StringIO(), StringIO()

    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        repl.ejecutar_codigo("var x = 5")
        repl.ejecutar_codigo(expresion)

    assert err_repl.getvalue() == ""
    assert out_repl.getvalue().strip().endswith(salida_esperada)


@pytest.mark.integration
def test_repl_fallback_expresion_sin_duplicar_salida_y_nameerror_real_preservado():
    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    out_repl, err_repl = StringIO(), StringIO()

    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        repl.ejecutar_codigo("var x = 5")
        repl.ejecutar_codigo("x + 10")

    lineas = [linea.strip() for linea in out_repl.getvalue().splitlines() if linea.strip()]
    assert err_repl.getvalue() == ""
    assert lineas == ["15"]

    with pytest.raises(NameError, match=r"^Variable no declarada: no_definida$"):
        repl.ejecutar_codigo("no_definida + 1")


@pytest.mark.integration
def test_repl_no_suprime_error_real_en_expresion_con_variable_no_declarada():
    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    out_repl, err_repl = StringIO(), StringIO()

    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        with pytest.raises(NameError, match=r"^Variable no declarada: x$"):
            repl.ejecutar_codigo("x + 10")

    assert out_repl.getvalue() == ""
    assert err_repl.getvalue() == ""


@pytest.mark.integration
def test_repl_statement_normal_imprimir_no_duplica_salida():
    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    out_repl, err_repl = StringIO(), StringIO()

    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        repl.ejecutar_codigo("var x = 5")
        repl.ejecutar_codigo("imprimir(x)")

    lineas_salida = [linea for linea in out_repl.getvalue().splitlines() if linea.strip()]
    assert err_repl.getvalue() == ""
    assert lineas_salida == ["5"]


@pytest.mark.integration
def test_repl_mantiene_estado_tras_error_intermedio():
    interpretador_cls = resolver_interpretador_cls(
        module_name="pcobra.cobra.cli.services.run_service",
        default_cls=InterpretadorCobra,
    )

    with patch.object(
        InterpretadorCobra,
        "_asegurar_no_autorreferencia_asignacion",
        return_value=None,
    ):
        setup_ok, _ = ejecutar_pipeline_explicito(
            PipelineInput(
                codigo="var x = 10",
                interpretador_cls=interpretador_cls,
                safe_mode=False,
                extra_validators=None,
            )
        )
        interpretador_persistente = setup_ok.interpretador

        with pytest.raises(Exception):  # noqa: BLE001 - contrato integración
            ejecutar_pipeline_explicito(
                PipelineInput(
                    codigo="var y = 10 / 0",
                    interpretador_cls=interpretador_cls,
                    safe_mode=False,
                    extra_validators=None,
                    interpretador=interpretador_persistente,
                )
            )

        out_repl, err_repl = StringIO(), StringIO()
        with redirect_stdout(out_repl), redirect_stderr(err_repl):
            setup_final, _ = ejecutar_pipeline_explicito(
                PipelineInput(
                    codigo="imprimir(x)",
                    interpretador_cls=interpretador_cls,
                    safe_mode=False,
                    extra_validators=None,
                    interpretador=interpretador_persistente,
                )
            )

    assert err_repl.getvalue() == ""
    assert out_repl.getvalue().strip().endswith("10")
    assert setup_final.interpretador.contextos[-1].get("x") == 10


@pytest.mark.integration
def test_repl_persistencia_entre_entradas_tras_error_intermedio_real() -> None:
    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    out_repl, err_repl = StringIO(), StringIO()

    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        repl.ejecutar_codigo("var x = 5")
        with pytest.raises(ZeroDivisionError):
            repl.ejecutar_codigo("var y = 10 / 0")
        repl.ejecutar_codigo("imprimir(x)")

    lineas = [linea.strip() for linea in out_repl.getvalue().splitlines() if linea.strip()]
    assert err_repl.getvalue() == ""
    assert lineas == ["5"]
    assert repl.interpretador.contextos[-1].get("x") == 5


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


@pytest.mark.integration
@pytest.mark.parametrize(
    "codigo_erroneo",
    [
        'imprimir("cadena sin cerrar)',
        "si verdadero imprimir(1)",
    ],
)
def test_error_sintactico_equivale_en_tipo_y_mensaje(codigo_erroneo):
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


@pytest.mark.integration
@pytest.mark.parametrize(
    ("caso", "prelude", "snippet", "variables_esperadas"),
    [
        (
            "mutacion_en_mientras_persiste",
            "var contador = 10",
            (
                "mientras verdadero:\n"
                "    contador = 15\n"
                "    romper\n"
                "fin"
            ),
            {"contador": 15},
        ),
        (
            "mutacion_en_mientras_persiste_fuera_del_bucle",
            "var total = 1",
            (
                "mientras verdadero:\n"
                "    total = 4\n"
                "    romper\n"
                "fin"
            ),
            {"total": 4},
        ),
        (
            "mientras_con_continuar_romper_y_variable_local_visible",
            "var paso = falso",
            (
                "mientras verdadero:\n"
                "    si paso:\n"
                "        var ultimo = 2\n"
                "        romper\n"
                "    fin\n"
                "    paso = verdadero\n"
                "    continuar\n"
                "fin"
            ),
            {"paso": True},
        ),
        (
            "bloque_anidado_shadowing_y_set_dirigido",
            "var raiz = 100",
            (
                "func ajustar():\n"
                "    var raiz = 5\n"
                "    raiz = 9\n"
                "    retorno raiz\n"
                "fin\n"
                "var resultado = ajustar()"
            ),
            {"raiz": 100, "resultado": 5},
        ),
    ],
)
def test_runtime_estado_final_paridad_run_vs_repl(
    caso: str,
    prelude: str,
    snippet: str,
    variables_esperadas: dict[str, int],
) -> None:
    resultado_script, resultado_repl = _run_pipeline_and_repl(
        prelude=prelude,
        snippet=snippet,
        variables_estado=tuple(variables_esperadas.keys()),
    )

    assert resultado_script["stderr"] == resultado_repl["stderr"] == "", (
        f"{caso}: no debe haber errores entre run y REPL"
    )
    assert resultado_script["estado"] == resultado_repl["estado"], (
        f"{caso}: el estado final del contexto debe ser equivalente"
    )
    assert resultado_script["estado"] == variables_esperadas, (
        f"{caso}: el estado final debe respetar semántica de scope esperada"
    )


@pytest.mark.integration
def test_sandbox_normaliza_safe_mode_y_validadores_igual_en_run_y_repl(monkeypatch):
    import pcobra.cobra.cli.services.run_service as run_service_module
    import pcobra.cobra.cli.commands.interactive_cmd as interactive_module

    class DummyInterp:
        def __init__(self, safe_mode=True, extra_validators=None):
            self.safe_mode = safe_mode
            self.extra_validators = extra_validators
            self.contextos = [{}]

        def ejecutar_ast(self, _ast):
            return None

        @staticmethod
        def _cargar_validadores(ruta):
            class _DummyValidador(ValidadorBase):
                pass

            validador = _DummyValidador()
            setattr(validador, "origen", ruta)
            return [validador]

    capturas: list[tuple[str, bool | None, object]] = []

    def _capturar_script(codigo, *, safe_mode=None, extra_validators=None, imprimir_resultado=False):
        capturas.append((codigo, safe_mode, extra_validators))
        return "print('ok')"

    monkeypatch.setattr(run_service_module, "InterpretadorCobra", DummyInterp)
    monkeypatch.setattr(interactive_module, "InterpretadorCobra", DummyInterp)
    monkeypatch.setattr(run_service_module, "construir_script_sandbox_canonico", _capturar_script)
    monkeypatch.setattr(interactive_module, "construir_script_sandbox_canonico", _capturar_script)
    monkeypatch.setattr(run_service_module, "ejecutar_en_sandbox", lambda *_args, **_kwargs: "")
    monkeypatch.setattr(interactive_module, "ejecutar_en_sandbox", lambda *_args, **_kwargs: "")

    servicio = RunService()
    rc = servicio.ejecutar_en_sandbox(
        "var valor = 1",
        seguro=1,
        extra_validators=["uno.py", "dos.py"],
    )
    repl = InteractiveCommand(DummyInterp())
    repl._seguro_repl = 1
    repl._extra_validators_repl = ["uno.py", "dos.py"]
    repl._ejecutar_en_sandbox("var valor = 1")

    assert rc == 0
    assert len(capturas) == 2
    assert capturas[0][1] is True and capturas[1][1] is True
    assert [getattr(v, "origen", None) for v in capturas[0][2]] == ["uno.py", "dos.py"]
    assert [getattr(v, "origen", None) for v in capturas[1][2]] == ["uno.py", "dos.py"]
