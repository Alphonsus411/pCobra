from __future__ import annotations

import argparse

from pcobra.cobra.cli.commands_v2 import repl_cmd as repl_module
from pcobra.cobra.core import ParserError, TipoToken


def _parser_error_incompleto(esperado):
    err = ParserError("entrada incompleta")
    err.esperado = [esperado]
    err.token_actual = type("Tok", (), {"tipo": TipoToken.EOF})()
    err.eof = True
    return err


def _args_repl() -> argparse.Namespace:
    return argparse.Namespace(
        sandbox=False,
        sandbox_docker=None,
        seguro=True,
        extra_validators=None,
        memory_limit=128,
        ignore_memory_limit=False,
    )


def test_repl_v2_contrato_llama_prevalidacion_y_pipeline_compartido(monkeypatch):
    command = repl_module.ReplCommandV2()
    entradas = iter(["var x = 1", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[tuple[str, bool]] = []
    runtime_alternativo_calls: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        return [object()]

    class _Setup:
        def __init__(self):
            self.interpretador = {}
            self.safe_mode = True
            self.validadores_extra = None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda pipeline_input, **_kwargs: pipeline_calls.append(
            (pipeline_input.codigo, pipeline_input.safe_mode)
        )
        or (_Setup(), None),
    )
    monkeypatch.setattr(
        command._delegate,
        "_ejecutar_en_sandbox",
        lambda _codigo: runtime_alternativo_calls.append("sandbox"),
    )
    monkeypatch.setattr(
        command._delegate,
        "_ejecutar_en_docker",
        lambda _codigo, _backend: runtime_alternativo_calls.append("docker"),
    )

    status = command.run(_args_repl())

    assert status == 0
    assert parse_calls == ["var x = 1"]
    assert pipeline_calls == [("var x = 1", True)]
    assert runtime_alternativo_calls == []


def test_repl_v2_persistencia_estado_var_x_e_imprimir_x(monkeypatch, capsys):
    command = repl_module.ReplCommandV2()
    entradas = iter(["var x = 10", "imprimir(x)", "exit"])
    estado: dict[str, int] = {}

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))
    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", lambda _codigo: [object()])
    monkeypatch.setattr(repl_module, "mostrar_info", lambda *_args, **_kwargs: None)

    class _Setup:
        def __init__(self, interpretador):
            self.interpretador = interpretador
            self.safe_mode = False
            self.validadores_extra = None

    class _Resultado:
        def __init__(self, valor):
            self.ast = [object()]
            self.resultado = valor

    def _fake_pipeline(pipeline_input, **_kwargs):
        interpretador = pipeline_input.interpretador or estado
        if pipeline_input.codigo == "var x = 10":
            interpretador["x"] = 10
            return _Setup(interpretador), _Resultado(None)
        assert pipeline_input.codigo == "imprimir(x)"
        return _Setup(interpretador), _Resultado(interpretador["x"])

    monkeypatch.setattr(repl_module, "ejecutar_pipeline_explicito", _fake_pipeline)

    status = command.run(_args_repl())

    assert status == 0
    assert capsys.readouterr().out == "10\n"


def test_repl_v2_bloque_anidado_real_mientras_si_fin_fin_acumula_hasta_completar(monkeypatch):
    command = repl_module.ReplCommandV2()
    entradas = iter(["mientras verdadero:", "si verdadero:", "fin", "fin", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    bloque_completo = "mientras verdadero:\nsi verdadero:\nfin\nfin"

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != bloque_completo:
            raise _parser_error_incompleto(TipoToken.FIN)
        return [object()]

    class _Setup:
        def __init__(self):
            self.interpretador = {}
            self.safe_mode = True
            self.validadores_extra = None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda pipeline_input, **_kwargs: pipeline_calls.append(pipeline_input.codigo)
        or (_Setup(), None),
    )

    status = command.run(_args_repl())

    assert status == 0
    assert parse_calls == [
        "mientras verdadero:",
        "mientras verdadero:\nsi verdadero:",
        "mientras verdadero:\nsi verdadero:\nfin",
        bloque_completo,
    ]
    assert pipeline_calls == [bloque_completo]


def test_repl_v2_error_sintactico_real_limpia_buffer_y_repl_sigue(monkeypatch):
    command = repl_module.ReplCommandV2()
    entradas = iter(["si verdadero:", "imprimir(1", "var ok = 1", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []
    errores_reportados: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo == "si verdadero:":
            raise _parser_error_incompleto(TipoToken.FIN)
        if codigo == "si verdadero:\nimprimir(1":
            raise ParserError("Token inesperado: '('")
        return [object()]

    class _Setup:
        def __init__(self):
            self.interpretador = {}
            self.safe_mode = True
            self.validadores_extra = None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        command._delegate,
        "_log_error",
        lambda _categoria, err: errores_reportados.append(str(err)),
    )
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda pipeline_input, **_kwargs: pipeline_calls.append(pipeline_input.codigo)
        or (_Setup(), None),
    )

    status = command.run(_args_repl())

    assert status == 0
    assert parse_calls == ["si verdadero:", "si verdadero:\nimprimir(1", "var ok = 1"]
    assert pipeline_calls == ["var ok = 1"]
    assert errores_reportados == ["Token inesperado: '('"]


def test_repl_v2_bloque_incompleto_no_ejecuta_ni_limpia_hasta_completar(monkeypatch):
    command = repl_module.ReplCommandV2()
    entradas = iter(["si verdadero:", "imprimir(1)", "fin", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    bloque_completo = "si verdadero:\nimprimir(1)\nfin"

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != bloque_completo:
            raise _parser_error_incompleto(TipoToken.FIN)
        return [object()]

    class _Setup:
        def __init__(self):
            self.interpretador = {}
            self.safe_mode = True
            self.validadores_extra = None

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        repl_module,
        "ejecutar_pipeline_explicito",
        lambda pipeline_input, **_kwargs: pipeline_calls.append(pipeline_input.codigo)
        or (_Setup(), None),
    )

    status = command.run(_args_repl())

    assert status == 0
    assert parse_calls == ["si verdadero:", "si verdadero:\nimprimir(1)", bloque_completo]
    assert pipeline_calls == [bloque_completo]
