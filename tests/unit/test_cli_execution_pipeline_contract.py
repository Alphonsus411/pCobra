from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from argparse import Namespace
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand
from pcobra.cobra.cli.execution_pipeline import PipelineInput, ejecutar_pipeline_explicito
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.core.runtime import InterpretadorCobra


def _args_execute(archivo: str) -> Namespace:
    return Namespace(
        archivo=archivo,
        debug=False,
        verbose=0,
        depurar=False,
        sandbox=False,
        contenedor=None,
        formatear=False,
        modo="mixto",
        seguro=False,
        extra_validators=None,
        allow_insecure_fallback=False,
    )


def _clasificar_error_execute(stderr: str) -> str | None:
    if "Error de análisis:" in stderr:
        return "analisis"
    if "Error ejecutando el script:" in stderr:
        return "semantico"
    if stderr.strip():
        return "otro"
    return None


def _clasificar_error_repl(exc: Exception | None) -> str | None:
    if exc is None:
        return None
    nombre = exc.__class__.__name__
    if nombre in {"LexerError", "ParserError"}:
        return "analisis"
    return "semantico"


def _run_execute_via_script(
    *,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    prelude: str,
    snippet: str,
    variable_persistente: str,
) -> dict[str, object]:
    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.execute_cmd.validar_dependencias", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        "pcobra.cobra.cli.commands.execute_cmd.limitar_cpu_segundos", lambda *_args, **_kwargs: None
    )
    codigo = "\n".join(
        [linea for linea in [prelude, snippet, f"var __probe = {variable_persistente}"] if linea]
    )
    archivo = tmp_path / "matriz_paridad.co"
    archivo.write_text(codigo, encoding="utf-8")
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = ExecuteCommand().run(_args_execute(str(archivo)))
    salida = out.getvalue()
    errores = err.getvalue()
    return {
        "rc": rc,
        "stdout": salida,
        "stderr": errores,
        "error_kind": _clasificar_error_execute(f"{salida}\n{errores}"),
    }


def _run_repl(
    *,
    prelude: str,
    snippet: str,
    variable_persistente: str,
) -> dict[str, object]:
    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    out, err = StringIO(), StringIO()
    exc: Exception | None = None
    with redirect_stdout(out), redirect_stderr(err):
        try:
            if prelude:
                repl.ejecutar_codigo(prelude)
            repl.ejecutar_codigo(snippet)
        except Exception as captured:  # noqa: BLE001 - contrato explícito entre rutas
            exc = captured
    persistente = None
    try:
        persistente = repl.interpretador.contextos[-1].get(variable_persistente)
    except Exception:  # noqa: BLE001 - el contrato compara estado observable entre rutas
        persistente = None
    return {
        "stdout": out.getvalue(),
        "stderr": err.getvalue(),
        "error_kind": _clasificar_error_repl(exc),
        "persistente": persistente,
    }


def _ultima_linea(salida: str) -> str:
    lineas = [linea.strip() for linea in salida.splitlines() if linea.strip()]
    return lineas[-1] if lineas else ""


def _normalizar_salida_repl(salida: str) -> str:
    lineas = [linea.strip() for linea in salida.splitlines() if linea.strip()]
    filtradas = [linea for linea in lineas if not linea.isdigit()]
    return "\n".join(filtradas)


@pytest.mark.parametrize(
    ("caso", "snippet"),
    [
        ("asignacion", "var persistente = 11"),
        ("condicional", "si verdadero:\n    var persistente = 12\nfin"),
        ("bucle", "mientras falso:\n    var temporal = 1\nfin"),
        (
            "anidacion_si_mientras_intentar",
            (
                "si verdadero:\n"
                "    mientras falso:\n"
                "        intentar:\n"
                "            var temporal = 1\n"
                "        capturar e:\n"
                "            var temporal = 2\n"
                "        fin\n"
                "    fin\n"
                "fin"
            ),
        ),
        (
            "define_local_en_funcion",
            (
                "func localiza():\n"
                "    var persistente = 33\n"
                "fin\n"
                "localiza()"
            ),
        ),
        ("funcion", "func incrementar(v):\n    retorno v + 3\nfin\nvar persistente = incrementar(10)"),
        ("error_semantico", "persistente = persistente + 1"),
    ],
)
def test_matriz_minima_paridad_execute_script_vs_repl(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caso: str, snippet: str
) -> None:
    prelude = "var persistente = 10"
    variable_persistente = "persistente"
    resultado_execute = _run_execute_via_script(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        prelude=prelude,
        snippet=snippet,
        variable_persistente=variable_persistente,
    )
    resultado_repl = _run_repl(
        prelude=prelude,
        snippet=snippet,
        variable_persistente=variable_persistente,
    )

    assert resultado_execute["error_kind"] == resultado_repl["error_kind"], (
        f"{caso}: tipo de error divergente entre rutas"
    )
    if resultado_repl["error_kind"] is None:
        assert _normalizar_salida_repl(str(resultado_repl["stdout"])) == str(
            resultado_execute["stdout"]
        ).strip(), f"{caso}: salida distinta entre ExecuteCommand (script) y REPL"
        assert resultado_execute["rc"] == 0, f"{caso}: ExecuteCommand debe finalizar en éxito"
        assert resultado_repl["persistente"] is not None, (
            f"{caso}: la variable persistente debe permanecer accesible en REPL"
        )
    else:
        assert resultado_execute["rc"] == 1, f"{caso}: ExecuteCommand debe reportar fallo"


def _args_interactive():
    return SimpleNamespace(
        seguro=False,
        extra_validators=None,
        sandbox=False,
        sandbox_docker=None,
        memory_limit=1024,
        ignore_memory_limit=True,
        allow_insecure_fallback=False,
    )


def test_contrato_resultado_igual_entre_modo_archivo_y_interactivo():
    codigo = "var x = 5\nimprimir(x)"

    cmd_execute = ExecuteCommand()
    with patch("sys.stdout", new_callable=StringIO) as out_file:
        result_file = cmd_execute._ejecutar_normal(codigo, seguro=False, extra_validators=None)

    cmd_interactive = InteractiveCommand(InterpretadorCobra())
    with patch("sys.stdout", new_callable=StringIO) as out_repl:
        cmd_interactive.ejecutar_codigo(codigo)

    assert result_file == 0
    assert out_file.getvalue() == out_repl.getvalue()


@pytest.mark.parametrize(
    ("caso", "codigo"),
    [
        (
            "mientras multilinea",
            "var x = 0\nmientras falso:\n    imprimir(99)\nfin\nimprimir(x)",
        ),
        (
            "si_sino multilinea",
            "var x = 2\nsi x < 1:\n    imprimir('menor')\nsino:\n    imprimir('mayor')\nfin",
        ),
        (
            "funcion con mutacion",
            "func incrementar(v):\n    retorno v + 1\nfin\nvar x = 1\nvar x = incrementar(x)\nimprimir(x)",
        ),
    ],
)
def test_contrato_salida_y_error_iguales_entre_execute_e_interactive(caso, codigo):
    cmd_execute = ExecuteCommand()
    out_execute, err_execute = StringIO(), StringIO()
    with redirect_stdout(out_execute), redirect_stderr(err_execute):
        rc_execute = cmd_execute._ejecutar_normal(codigo, seguro=False, extra_validators=None)

    cmd_interactive = InteractiveCommand(InterpretadorCobra())
    out_repl, err_repl = StringIO(), StringIO()
    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        cmd_interactive.ejecutar_codigo(codigo)

    assert rc_execute == 0, f"{caso}: execute devolvió código distinto de 0"
    assert out_execute.getvalue() == out_repl.getvalue(), f"{caso}: salida divergente"
    assert err_execute.getvalue() == err_repl.getvalue(), f"{caso}: error divergente"


def test_contrato_error_igual_entre_modo_archivo_y_interactivo():
    codigo_invalido = "si verdadero:\nimprimir(1)"

    cmd_execute = ExecuteCommand()
    cmd_interactive = InteractiveCommand(InterpretadorCobra())

    with pytest.raises(Exception) as err_execute:
        cmd_execute._analizar_codigo(codigo_invalido)

    with pytest.raises(Exception) as err_interactive:
        cmd_interactive.procesar_ast(codigo_invalido)

    assert type(err_execute.value) is type(err_interactive.value)
    assert str(err_execute.value) == str(err_interactive.value)


@pytest.mark.parametrize(
    ("codigo_invalido", "caso"),
    [
        ("si verdadero:\nimprimir(1)\nfin", "condicional válido con ':'"),
        ("si verdadero\nimprimir(1)\nfin", "condicional sin ':'"),
        ("si verdadero:\nimprimir(1)", "condicional sin 'fin'"),
    ],
)
def test_contrato_pipeline_error_y_mensaje_entre_no_interactivo_y_repl(
    codigo_invalido, caso
):
    cmd_execute = ExecuteCommand()
    cmd_interactive = InteractiveCommand(InterpretadorCobra())

    def _capturar_error_no_interactivo():
        try:
            cmd_execute._analizar_codigo(codigo_invalido)
            return None
        except Exception as exc:  # noqa: BLE001 - contrato explícito del test
            return exc

    def _capturar_error_repl():
        try:
            cmd_interactive.ejecutar_codigo(codigo_invalido)
            return None
        except Exception as exc:  # noqa: BLE001 - contrato explícito del test
            return exc

    err_execute = _capturar_error_no_interactivo()
    err_repl = _capturar_error_repl()

    assert type(err_execute) is type(err_repl), f"{caso}: tipo de error divergente"
    assert str(err_execute) == str(err_repl), f"{caso}: mensaje de error divergente"


def test_repl_ejecuta_bloque_completo_sin_parseo_parcial_por_linea():
    inputs = ["si verdadero:", "imprimir(1)", "fin", "salir"]
    cmd = InteractiveCommand(MagicMock())

    with patch("pcobra.cobra.cli.commands.interactive_cmd.validar_dependencias"), patch(
        "prompt_toolkit.PromptSession.prompt", side_effect=inputs
    ), patch.object(
        cmd,
        "ejecutar_codigo",
    ) as mock_ejecutar_codigo:
        ret = cmd.run(_args_interactive())

    assert ret == 0
    mock_ejecutar_codigo.assert_called_once_with("si verdadero:\nimprimir(1)\nfin", None)


def test_paridad_repl_script_mientras_con_mutacion_persistente_mismo_entorno():
    cmd_execute = ExecuteCommand()
    out_script, err_script = StringIO(), StringIO()
    codigo_script = (
        "var base = 0\n"
        "mientras falso:\n"
        "    pasar\n"
        "fin\n"
        "var acumulado = 42"
    )
    with redirect_stdout(out_script), redirect_stderr(err_script):
        rc_script = cmd_execute._ejecutar_normal(codigo_script, seguro=False, extra_validators=None)

    cmd_interactive = InteractiveCommand(InterpretadorCobra())
    out_repl, err_repl = StringIO(), StringIO()
    with redirect_stdout(out_repl), redirect_stderr(err_repl):
        cmd_interactive.ejecutar_codigo(
            "var base = 0\nmientras falso:\n    pasar\nfin"
        )
        cmd_interactive.ejecutar_codigo("var acumulado = 42")

    assert rc_script == 0
    assert out_script.getvalue() == ""
    assert err_script.getvalue() == err_repl.getvalue() == ""
    assert cmd_interactive.interpretador.contextos[-1].get("base") == 0
    assert cmd_interactive.interpretador.contextos[-1].get("acumulado") == 42


def test_contrato_repl_igual_script_estado_final_con_bucles_y_asignaciones():
    codigo = (
        "var base = 0\n"
        "mientras falso:\n"
        "    pasar\n"
        "fin\n"
        "var acumulado = 42\n"
        "var ultimo = 42"
    )
    setup_script, _ = ejecutar_pipeline_explicito(
        PipelineInput(
            codigo=codigo,
            interpretador_cls=InterpretadorCobra,
            safe_mode=False,
            extra_validators=None,
        )
    )
    contexto_script = setup_script.interpretador.contextos[-1]

    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    repl.ejecutar_codigo(codigo)
    estado_repl = repl.interpretador.contextos[-1]

    assert estado_repl.values == contexto_script.values
    assert estado_repl.get("base") == 0

