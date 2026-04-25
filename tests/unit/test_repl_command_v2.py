import argparse

from cobra.cli.commands_v2.repl_cmd import ReplCommandV2
from pcobra.cobra.core import ParserError


def test_es_error_de_bloque_incompleto_por_mensajes_parser():
    command = ReplCommandV2()

    assert command.es_error_de_bloque_incompleto(
        ParserError("Se esperaba 'fin' para cerrar el bloque condicional")
    )
    assert command.es_error_de_bloque_incompleto(
        ParserError("Token inesperado en término: TipoToken.EOF")
    )
    assert command.es_error_de_bloque_incompleto(
        ParserError("Se esperaba ']' al final de la lista")
    )
    assert not command.es_error_de_bloque_incompleto(
        ParserError("Se encontró 'fin' inesperado")
    )
    assert not command.es_error_de_bloque_incompleto(ValueError("no parser"))


def test_repl_v2_mantiene_buffer_hasta_parseo_valido(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["si verdadero:", "imprimir(1)", "fin", "exit"])
    parse_calls: list[str] = []
    executed: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != "si verdadero:\nimprimir(1)\nfin":
            raise ParserError("Se esperaba 'fin' para cerrar el bloque condicional")
        return []

    monkeypatch.setattr("cobra.cli.commands_v2.repl_cmd.prevalidar_y_parsear_codigo", _fake_parse)
    class _Setup:
        def __init__(self, safe_mode, validadores_extra):
            self.interpretador = object()
            self.safe_mode = safe_mode
            self.validadores_extra = validadores_extra

    def _fake_pipeline(pipeline_input, **_kwargs):
        executed.append(pipeline_input.codigo)
        return _Setup(pipeline_input.safe_mode, pipeline_input.extra_validators), None

    monkeypatch.setattr("cobra.cli.commands_v2.repl_cmd.ejecutar_pipeline_explicito", _fake_pipeline)

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


def test_repl_v2_limpia_buffer_ante_error_real(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["algo_mal", "exit"])
    parse_calls: list[str] = []
    logged: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        raise ParserError("Se encontró 'fin' inesperado")

    monkeypatch.setattr("cobra.cli.commands_v2.repl_cmd.prevalidar_y_parsear_codigo", _fake_parse)
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

    monkeypatch.setattr("cobra.cli.commands_v2.repl_cmd.ejecutar_pipeline_explicito", _fake_pipeline)
    monkeypatch.setattr("cobra.cli.commands_v2.repl_cmd.prevalidar_y_parsear_codigo", lambda _codigo: [])

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
