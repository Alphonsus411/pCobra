import argparse

import pytest

from pcobra.cobra.cli.commands_v2 import repl_cmd as repl_module
from pcobra.cobra.cli.commands import interactive_cmd as interactive_module
from pcobra.cobra.core import ParserError, TipoToken

ReplCommandV2 = repl_module.ReplCommandV2


def _parser_error_con_metadata(
    mensaje: str,
    *,
    esperado=None,
    token_actual=None,
    eof: bool | None = None,
    posicion: int | None = None,
):
    err = ParserError(mensaje)
    if esperado is not None:
        err.esperado = esperado
    if token_actual is not None:
        err.token_actual = token_actual
    if eof is not None:
        err.eof = eof
    if posicion is not None:
        err.posicion = posicion
    return err


@pytest.mark.parametrize(
    ("mensaje", "es_incompleto"),
    [
        ("Se esperaba 'fin' para cerrar el bloque condicional", True),
        ("Token inesperado en término: TipoToken.EOF", False),
        ("Se esperaba ']' al final de la lista", False),
        ("Token inesperado: '('", False),
        ("Se encontró 'fin' inesperado", False),
    ],
)
def test_es_error_de_bloque_incompleto_fallback_textual_cubre_variantes_parser(mensaje, es_incompleto):
    command = ReplCommandV2()
    assert command.es_error_de_bloque_incompleto(ParserError(mensaje)) is es_incompleto


def test_es_error_de_bloque_incompleto_rechaza_excepciones_que_no_son_parser():
    command = ReplCommandV2()
    assert not command.es_error_de_bloque_incompleto(ValueError("no parser"))


@pytest.mark.parametrize(
    ("err", "es_incompleto"),
    [
        (
            _parser_error_con_metadata(
                "bloque sin cierre",
                esperado=[TipoToken.FIN],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
                posicion=15,
            ),
            True,
        ),
        (
            _parser_error_con_metadata(
                "paren sin cierre",
                esperado=[TipoToken.RPAREN],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
                posicion=8,
            ),
            True,
        ),
        (
            _parser_error_con_metadata(
                "lista sin cierre",
                esperado=[TipoToken.RBRACKET],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
                posicion=3,
            ),
            True,
        ),
        (
            _parser_error_con_metadata(
                "dict sin cierre",
                esperado=[TipoToken.RBRACE],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
                posicion=21,
            ),
            True,
        ),
        (
            _parser_error_con_metadata(
                "EOF prematuro",
                esperado=[TipoToken.RPAREN],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
                posicion=1,
            ),
            True,
        ),
        (
            _parser_error_con_metadata(
                "error real",
                esperado=[TipoToken.IDENTIFICADOR],
                token_actual=type("Tok", (), {"tipo": TipoToken.SI})(),
                eof=False,
                posicion=4,
            ),
            False,
        ),
    ],
)
def test_es_error_de_bloque_incompleto_prioriza_metadata(err, es_incompleto):
    command = ReplCommandV2()
    assert command.es_error_de_bloque_incompleto(err) is es_incompleto


@pytest.mark.parametrize(
    ("atributos", "es_incompleto"),
    [
        (
            {
                "expected_tokens": [TipoToken.FIN],
                "token_type": TipoToken.EOF,
                "unexpected_eof": True,
            },
            True,
        ),
        (
            {
                "expected_types": [TipoToken.RPAREN],
                "current_token_type": TipoToken.EOF,
            },
            True,
        ),
        (
            {
                "expected_terminals": [TipoToken.RBRACKET],
                "actual_token_type": TipoToken.EOF,
                "is_eof": True,
            },
            True,
        ),
        (
            {
                "esperados": [TipoToken.RBRACE],
                "last_token_type": TipoToken.EOF,
                "is_unexpected_eof": True,
            },
            True,
        ),
        (
            {
                "expected": [TipoToken.FIN],
                "token_type": TipoToken.EOF,
                "unexpected_eof": False,
            },
            True,
        ),
        (
            {
                "expected": [TipoToken.FIN],
                "unexpected_eof": True,
            },
            True,
        ),
        (
            {
                "expected": [TipoToken.FIN],
            },
            False,
        ),
        (
            {
                "expected": [TipoToken.IDENTIFICADOR],
                "current_token_type": TipoToken.EOF,
                "unexpected_eof": True,
            },
            False,
        ),
    ],
)
def test_es_error_de_bloque_incompleto_con_metadata_parcial(atributos, es_incompleto):
    command = ReplCommandV2()
    err = ParserError("metadata parcial")
    for nombre, valor in atributos.items():
        setattr(err, nombre, valor)
    assert command.es_error_de_bloque_incompleto(err) is es_incompleto


def test_extrae_token_desde_state_con_alias_de_parser_real():
    command = ReplCommandV2()
    err = ParserError("metadata state")
    err.state = type("State", (), {"actual_token": type("Tok", (), {"tipo": TipoToken.EOF})()})()
    token = command._extraer_token_desde_error(err)
    assert token is not None
    assert token.tipo == TipoToken.EOF


def test_extrae_token_desde_unexpected_token_si_no_hay_token_actual():
    command = ReplCommandV2()
    err = ParserError("metadata unexpected token")
    err.unexpected_token = type("Tok", (), {"tipo": TipoToken.EOF})()
    token = command._extraer_token_desde_error(err)
    assert token is not None
    assert token.tipo == TipoToken.EOF


def test_incompleto_bloque_simple_por_eof_inesperado_y_fin_pendiente():
    command = ReplCommandV2()
    err = _parser_error_con_metadata(
        "bloque sin cierre",
        esperado=[TipoToken.FIN],
        token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
        eof=True,
    )
    assert command.es_error_de_bloque_incompleto(err) is True


def test_incompleto_bloque_anidado_por_eof_inesperado_y_cierres_pendientes():
    command = ReplCommandV2()
    err = _parser_error_con_metadata(
        "bloque anidado sin cierres",
        esperado=[TipoToken.RPAREN, TipoToken.FIN],
        token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
        eof=True,
    )
    assert command.es_error_de_bloque_incompleto(err) is True


def test_error_sintactico_real_no_se_clasifica_como_incompleto():
    command = ReplCommandV2()
    err = _parser_error_con_metadata(
        "token inesperado real",
        esperado=[TipoToken.IDENTIFICADOR],
        token_actual=type("Tok", (), {"tipo": TipoToken.SI})(),
        eof=False,
    )
    assert command.es_error_de_bloque_incompleto(err) is False


def test_repl_v2_mantiene_buffer_hasta_parseo_valido(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["si verdadero:", "imprimir(1)", "fin", "exit"])
    parse_calls: list[str] = []
    executed: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != "si verdadero:\nimprimir(1)\nfin":
            raise _parser_error_con_metadata(
                "Se esperaba 'fin' para cerrar el bloque condicional",
                esperado=[TipoToken.FIN],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
            )
        return []

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    class _Setup:
        def __init__(self, safe_mode, validadores_extra):
            self.interpretador = object()
            self.safe_mode = safe_mode
            self.validadores_extra = validadores_extra

    def _fake_pipeline(pipeline_input, **_kwargs):
        executed.append(pipeline_input.codigo)
        return _Setup(pipeline_input.safe_mode, pipeline_input.extra_validators), None

    monkeypatch.setattr(repl_module, "ejecutar_pipeline_explicito", _fake_pipeline)

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert parse_calls == [
        "si verdadero:",
        "si verdadero:\nimprimir(1)",
        "si verdadero:\nimprimir(1)\nfin",
    ]
    assert executed == ["si verdadero:\nimprimir(1)\nfin"]


def test_repl_v2_prompts_primario_y_secundario_en_bloque(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["si verdadero:", "imprimir(1)", "fin", "exit"])
    prompts: list[str] = []

    def _fake_input(prompt: str) -> str:
        prompts.append(prompt)
        return next(entradas)

    monkeypatch.setattr("builtins.input", _fake_input)

    def _fake_parse(codigo: str):
        if codigo != "si verdadero:\nimprimir(1)\nfin":
            raise _parser_error_con_metadata(
                "Se esperaba 'fin' para cerrar el bloque condicional",
                esperado=[TipoToken.FIN],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
            )
        return []

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)

    class _Setup:
        def __init__(self):
            self.interpretador = object()
            self.safe_mode = False
            self.validadores_extra = None

    monkeypatch.setattr(
        repl_module, "ejecutar_pipeline_explicito", lambda *_args, **_kwargs: (_Setup(), None)
    )

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert prompts == [">>> ", "... ", "... ", ">>> "]


def test_repl_v2_bloque_si_x_mayor_que_5_acumula_hasta_fin_y_muestra_prompt_secundario(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["si x > 5:", "imprimir(x)", "fin", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []
    prompts: list[str] = []

    def _fake_input(prompt: str) -> str:
        prompts.append(prompt)
        return next(entradas)

    monkeypatch.setattr("builtins.input", _fake_input)

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != "si x > 5:\nimprimir(x)\nfin":
            raise _parser_error_con_metadata(
                "Se esperaba 'fin' para cerrar el bloque condicional",
                esperado=[TipoToken.FIN],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
            )
        return []

    class _Setup:
        def __init__(self):
            self.interpretador = object()
            self.safe_mode = False
            self.validadores_extra = None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda pipeline_input, **_kwargs: pipeline_calls.append(pipeline_input.codigo)
        or (_Setup(), None),
    )

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert parse_calls == ["si x > 5:", "si x > 5:\nimprimir(x)", "si x > 5:\nimprimir(x)\nfin"]
    assert pipeline_calls == ["si x > 5:\nimprimir(x)\nfin"]
    assert prompts == [">>> ", "... ", "... ", ">>> "]


def test_repl_v2_sale_por_salir_y_por_exit(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["salir"])
    prompts_salir: list[str] = []

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: prompts_salir.append(prompt) or next(entradas),
    )
    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", lambda _codigo: [])
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("no debe ejecutar")),
    )

    status_salir = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )
    assert status_salir == 0
    assert prompts_salir == [">>> "]

    command = ReplCommandV2()
    entradas_exit = iter(["exit"])
    prompts_exit: list[str] = []
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: prompts_exit.append(prompt) or next(entradas_exit),
    )
    status_exit = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )
    assert status_exit == 0
    assert prompts_exit == [">>> "]


@pytest.mark.parametrize("comando_salida", ["exit", "salir"])
def test_repl_v2_salida_cancela_bloque_pendiente_de_forma_explicita(monkeypatch, comando_salida):
    command = ReplCommandV2()
    entradas = iter(["si verdadero:", comando_salida, "fin", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        raise _parser_error_con_metadata(
            "Se esperaba 'fin' para cerrar el bloque condicional",
            esperado=[TipoToken.FIN],
            token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
            eof=True,
        )

    class _Setup:
        def __init__(self):
            self.interpretador = object()
            self.safe_mode = False
            self.validadores_extra = None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda pipeline_input, **_kwargs: pipeline_calls.append(pipeline_input.codigo)
        or (_Setup(), None),
    )

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert parse_calls == ["si verdadero:"]
    assert pipeline_calls == []


def test_repl_v2_limpia_buffer_ante_error_real(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["algo_mal", "exit"])
    parse_calls: list[str] = []
    logged: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        raise ParserError("Se encontró 'fin' inesperado")

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(command._delegate, "_log_error", lambda _cat, err: logged.append(str(err)))

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert parse_calls == ["algo_mal"]
    assert logged == ["Se encontró 'fin' inesperado"]


@pytest.mark.parametrize(
    ("entradas", "errores_por_codigo", "parse_esperado", "pipeline_esperado", "errores_esperados"),
    [
        (
            ["si verdadero :", "fin", "exit"],
            {
                "si verdadero :": _parser_error_con_metadata(
                    "Se esperaba 'fin' para cerrar el bloque condicional",
                    esperado=[TipoToken.FIN],
                    token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                    eof=True,
                ),
            },
            ["si verdadero :", "si verdadero :\nfin"],
            ["si verdadero :\nfin"],
            [],
        ),
        (
            ["mientras verdadero :", "fin", "exit"],
            {
                "mientras verdadero :": _parser_error_con_metadata(
                    "Se esperaba 'fin' para cerrar el bloque mientras",
                    esperado=[TipoToken.FIN],
                    token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                    eof=True,
                ),
            },
            ["mientras verdadero :", "mientras verdadero :\nfin"],
            ["mientras verdadero :\nfin"],
            [],
        ),
        (
            ["si verdadero :", "imprimir(1", "var z = 9", "exit"],
            {
                "si verdadero :": _parser_error_con_metadata(
                    "Se esperaba 'fin' para cerrar el bloque condicional",
                    esperado=[TipoToken.FIN],
                    token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                    eof=True,
                ),
                "si verdadero :\nimprimir(1": "Token inesperado: '('",
            },
            ["si verdadero :", "si verdadero :\nimprimir(1", "var z = 9"],
            ["var z = 9"],
            ["Token inesperado: '('"],
        ),
    ],
    ids=[
        "incompleto_si_conserva_buffer",
        "incompleto_mientras_conserva_buffer",
        "error_real_limpia_buffer",
    ],
)
def test_repl_v2_incompleto_vs_error_real_buffer(
    monkeypatch,
    entradas,
    errores_por_codigo,
    parse_esperado,
    pipeline_esperado,
    errores_esperados,
):
    command = ReplCommandV2()
    entradas_iter = iter(entradas)
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []
    logged: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas_iter))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo in errores_por_codigo:
            err = errores_por_codigo[codigo]
            if isinstance(err, ParserError):
                raise err
            raise ParserError(err)
        return []

    class _Setup:
        def __init__(self):
            self.interpretador = object()
            self.safe_mode = False
            self.validadores_extra = None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda pipeline_input, **_kwargs: pipeline_calls.append(pipeline_input.codigo)
        or (_Setup(), None),
    )
    monkeypatch.setattr(command._delegate, "_log_error", lambda _cat, err: logged.append(str(err)))

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert parse_calls == parse_esperado
    assert pipeline_calls == pipeline_esperado
    assert logged == errores_esperados


def test_repl_v2_linea_en_blanco_no_ejecuta_ni_resetea_estado_global(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["var x = 1", "   ", "imprimir(x)", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []
    estado: dict[str, int] = {}

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    class _Setup:
        def __init__(self, interpretador):
            self.interpretador = interpretador
            self.safe_mode = False
            self.validadores_extra = None

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        return []

    def _fake_pipeline(pipeline_input, **_kwargs):
        pipeline_calls.append(pipeline_input.codigo)
        interpretador = pipeline_input.interpretador or estado
        if pipeline_input.codigo == "var x = 1":
            interpretador["x"] = 1
        if pipeline_input.codigo == "imprimir(x)":
            assert interpretador["x"] == 1
        return _Setup(interpretador), None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(repl_module, "ejecutar_pipeline_explicito", _fake_pipeline)

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert parse_calls == ["var x = 1", "imprimir(x)"]
    assert pipeline_calls == ["var x = 1", "imprimir(x)"]


def test_repl_v2_error_sintaxis_real_limpia_buffer_y_continua(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["si verdadero:", "imprimir(1", "var z = 9", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []
    logged: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo == "si verdadero:":
            raise _parser_error_con_metadata(
                "Se esperaba 'fin' para cerrar el bloque condicional",
                esperado=[TipoToken.FIN],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
            )
        if codigo == "si verdadero:\nimprimir(1":
            raise ParserError("Token inesperado: '('")
        return []

    class _Setup:
        def __init__(self):
            self.interpretador = object()
            self.safe_mode = False
            self.validadores_extra = None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda pipeline_input, **_kwargs: pipeline_calls.append(pipeline_input.codigo)
        or (_Setup(), None),
    )
    monkeypatch.setattr(command._delegate, "_log_error", lambda _cat, err: logged.append(str(err)))

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert parse_calls == ["si verdadero:", "si verdadero:\nimprimir(1", "var z = 9"]
    assert pipeline_calls == ["var z = 9"]
    assert logged == ["Token inesperado: '('"]


def test_repl_v2_error_sintactico_real_limpia_buffer_y_permite_entrada_nueva(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["si x > 5:", "imprimir(", "var y = 7", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []
    logged: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo == "si x > 5:":
            raise _parser_error_con_metadata(
                "Se esperaba 'fin' para cerrar el bloque condicional",
                esperado=[TipoToken.FIN],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
            )
        if codigo == "si x > 5:\nimprimir(":
            raise ParserError("Token inesperado en término: TipoToken.EOF")
        return []

    class _Setup:
        def __init__(self):
            self.interpretador = object()
            self.safe_mode = False
            self.validadores_extra = None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda pipeline_input, **_kwargs: pipeline_calls.append(pipeline_input.codigo)
        or (_Setup(), None),
    )
    monkeypatch.setattr(command._delegate, "_log_error", lambda _cat, err: logged.append(str(err)))

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert parse_calls == ["si x > 5:", "si x > 5:\nimprimir(", "var y = 7"]
    assert pipeline_calls == ["var y = 7"]
    assert logged == ["Token inesperado en término: TipoToken.EOF"]


def test_repl_v2_fallback_mensaje_se_esperaba_fin_sin_metadata_completa(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["si x > 5:", "imprimir(x)", "fin", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != "si x > 5:\nimprimir(x)\nfin":
            raise ParserError("Se esperaba 'fin' para cerrar bloque al final de entrada")
        return []

    class _Setup:
        def __init__(self):
            self.interpretador = object()
            self.safe_mode = False
            self.validadores_extra = None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda pipeline_input, **_kwargs: pipeline_calls.append(pipeline_input.codigo)
        or (_Setup(), None),
    )

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert parse_calls == ["si x > 5:", "si x > 5:\nimprimir(x)", "si x > 5:\nimprimir(x)\nfin"]
    assert pipeline_calls == ["si x > 5:\nimprimir(x)\nfin"]


def test_repl_v2_error_ejecucion_limpia_buffer_actual_y_continua(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["si verdadero:", "fin", "var z = 9", "exit"])
    pipeline_calls: list[str] = []
    logged: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        if codigo == "si verdadero:":
            raise _parser_error_con_metadata(
                "Se esperaba 'fin' para cerrar el bloque condicional",
                esperado=[TipoToken.FIN],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
            )
        return []

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)

    class _Setup:
        def __init__(self):
            self.interpretador = object()
            self.safe_mode = False
            self.validadores_extra = None

    def _fake_pipeline(pipeline_input, **_kwargs):
        pipeline_calls.append(pipeline_input.codigo)
        if pipeline_input.codigo == "si verdadero:\nfin":
            raise RuntimeError("falló ejecución")
        return _Setup(), None

    monkeypatch.setattr(repl_module, "ejecutar_pipeline_explicito", _fake_pipeline)
    monkeypatch.setattr(command._delegate, "_log_error", lambda _cat, err: logged.append(str(err)))

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert pipeline_calls == ["si verdadero:\nfin", "var z = 9"]
    assert logged == ["falló ejecución"]


def test_repl_v2_persiste_interpretador_entre_bloques(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["var x = 10", "imprimir(x)", "exit"])
    interpretadores_recibidos = []
    estado: dict[str, int] = {}

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    class _Setup:
        def __init__(self, interpretador):
            self.interpretador = interpretador
            self.safe_mode = False
            self.validadores_extra = None

    def _fake_pipeline(pipeline_input, **_kwargs):
        interpretadores_recibidos.append(pipeline_input.interpretador)
        interpretador = pipeline_input.interpretador or estado
        if pipeline_input.codigo.strip() == "var x = 10":
            interpretador["x"] = 10
        if pipeline_input.codigo.strip() == "imprimir(x)":
            assert interpretador["x"] == 10
        return _Setup(interpretador), None

    monkeypatch.setattr(repl_module, "ejecutar_pipeline_explicito", _fake_pipeline)
    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", lambda _codigo: [])

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            seguro=False,
            extra_validators=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert interpretadores_recibidos == [None, estado]


def test_repl_v2_anidamiento_real_no_ejecuta_hasta_cierre_completo_y_persiste_estado(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(
        [
            "mientras verdadero:",
            "si verdadero:",
            "var total = 5",
            "romper",
            "fin",
            "fin",
            "imprimir(total)",
            "exit",
        ]
    )
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []
    interpretadores_recibidos: list[dict[str, int] | None] = []
    estado: dict[str, int] = {}

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo not in {
            "mientras verdadero:\nsi verdadero:\nvar total = 5\nromper\nfin\nfin",
            "imprimir(total)",
        }:
            raise _parser_error_con_metadata(
                "Se esperaba 'fin' para cerrar el bloque condicional",
                esperado=[TipoToken.FIN],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
            )
        return []

    class _Setup:
        def __init__(self, interpretador):
            self.interpretador = interpretador
            self.safe_mode = False
            self.validadores_extra = None

    def _fake_pipeline(pipeline_input, **_kwargs):
        pipeline_calls.append(pipeline_input.codigo)
        interpretadores_recibidos.append(pipeline_input.interpretador)
        interpretador = pipeline_input.interpretador or estado
        if pipeline_input.codigo.startswith("mientras verdadero:"):
            interpretador["total"] = 5
        if pipeline_input.codigo == "imprimir(total)":
            assert interpretador["total"] == 5
        return _Setup(interpretador), None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(repl_module, "ejecutar_pipeline_explicito", _fake_pipeline)

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            seguro=False,
            extra_validators=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert parse_calls == [
        "mientras verdadero:",
        "mientras verdadero:\nsi verdadero:",
        "mientras verdadero:\nsi verdadero:\nvar total = 5",
        "mientras verdadero:\nsi verdadero:\nvar total = 5\nromper",
        "mientras verdadero:\nsi verdadero:\nvar total = 5\nromper\nfin",
        "mientras verdadero:\nsi verdadero:\nvar total = 5\nromper\nfin\nfin",
        "imprimir(total)",
    ]
    assert pipeline_calls == [
        "mientras verdadero:\nsi verdadero:\nvar total = 5\nromper\nfin\nfin",
        "imprimir(total)",
    ]
    assert interpretadores_recibidos == [None, estado]


@pytest.mark.parametrize(
    ("entrada", "resultado", "ast", "salida_esperada"),
    [
        ("imprimir('hola')", None, [object()], ""),
        ("1 + 1", 2, [object()], "2\n"),
    ],
    ids=["sentencia-imprimir-no-duplica", "expresion-simple-con-echo"],
)
def test_repl_v2_salida_homogenea_para_sentencia_y_expresion(
    monkeypatch, capsys, entrada, resultado, ast, salida_esperada
):
    command = ReplCommandV2()
    entradas = iter([entrada, "exit"])

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))
    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", lambda _codigo: ast)
    monkeypatch.setattr(repl_module, "mostrar_info", lambda *_args, **_kwargs: None)

    class _Setup:
        def __init__(self):
            self.interpretador = object()
            self.safe_mode = False
            self.validadores_extra = None

    class _Resultado:
        def __init__(self):
            self.ast = ast
            self.resultado = resultado

    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda *_args, **_kwargs: (_Setup(), _Resultado()),
    )

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert capsys.readouterr().out == salida_esperada


def test_repl_v2_no_hace_echo_automatico_para_estructuras_de_control(monkeypatch, capsys):
    command = ReplCommandV2()
    entradas = iter(["si verdadero:\nfin", "exit"])

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))
    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", lambda _codigo: [object()])
    monkeypatch.setattr(repl_module, "mostrar_info", lambda *_args, **_kwargs: None)

    class _Setup:
        def __init__(self):
            self.interpretador = object()
            self.safe_mode = False
            self.validadores_extra = None

    class _Resultado:
        def __init__(self):
            self.ast = [interactive_module.NodoCondicional(True, [], [])]
            self.resultado = "resultado-interno"

    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda *_args, **_kwargs: (_Setup(), _Resultado()),
    )

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert capsys.readouterr().out == ""


def test_repl_v2_var_e_imprimir_persisten_estado_y_muestran_valor(monkeypatch, capsys):
    command = ReplCommandV2()
    entradas = iter(["var x = 10", "imprimir(x)", "exit"])
    estado: dict[str, int] = {}

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))
    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", lambda _codigo: [object()])

    class _Setup:
        def __init__(self, interpretador):
            self.interpretador = interpretador
            self.safe_mode = False
            self.validadores_extra = None

    class _Resultado:
        def __init__(self, ast, resultado):
            self.ast = ast
            self.resultado = resultado

    def _fake_pipeline(pipeline_input, **_kwargs):
        interpretador = pipeline_input.interpretador or estado
        if pipeline_input.codigo == "var x = 10":
            interpretador["x"] = 10
            return _Setup(interpretador), _Resultado([object()], None)
        assert pipeline_input.codigo == "imprimir(x)"
        return _Setup(interpretador), _Resultado([object()], interpretador["x"])

    monkeypatch.setattr(repl_module, "ejecutar_pipeline_explicito", _fake_pipeline)
    monkeypatch.setattr(repl_module, "mostrar_info", lambda *_args, **_kwargs: None)

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert capsys.readouterr().out == "10\n"


def test_repl_v2_bloque_incompleto_acumula_buffer_y_sesion_sigue_activa(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["si verdadero:", "imprimir(1)", "fin", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != "si verdadero:\nimprimir(1)\nfin":
            raise _parser_error_con_metadata(
                "Se esperaba 'fin' para cerrar el bloque condicional",
                esperado=[TipoToken.FIN],
                token_actual=type("Tok", (), {"tipo": TipoToken.EOF})(),
                eof=True,
            )
        return []

    class _Setup:
        def __init__(self):
            self.interpretador = {}
            self.safe_mode = False
            self.validadores_extra = None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda pipeline_input, **_kwargs: pipeline_calls.append(pipeline_input.codigo)
        or (_Setup(), None),
    )

    status = command.run(
        argparse.Namespace(
            sandbox=False,
            sandbox_docker=None,
            memory_limit=128,
            ignore_memory_limit=False,
        )
    )

    assert status == 0
    assert parse_calls == [
        "si verdadero:",
        "si verdadero:\nimprimir(1)",
        "si verdadero:\nimprimir(1)\nfin",
    ]
    assert pipeline_calls == ["si verdadero:\nimprimir(1)\nfin"]
