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
    ejecucion_calls: list[str] = []
    runtime_alternativo_calls: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        return [object()]

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        command._delegate,
        "ejecutar_codigo",
        lambda codigo: ejecucion_calls.append(codigo),
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
    assert ejecucion_calls == ["var x = 1"]
    assert runtime_alternativo_calls == []


def test_repl_v2_ejecutar_modo_normal_delega_parseo_al_delegate(monkeypatch):
    command = repl_module.ReplCommandV2()
    called: dict[str, object] = {}

    def _fake_delegate(codigo: str, prevalidar_fn):
        called["codigo"] = codigo
        called["prevalidar_fn"] = prevalidar_fn

    monkeypatch.setattr(
        command._delegate,
        "parsear_y_ejecutar_codigo_repl",
        _fake_delegate,
    )

    command._ejecutar_en_modo_normal("imprimir(1)", object)

    assert called == {
        "codigo": "imprimir(1)",
        "prevalidar_fn": repl_module.prevalidar_y_parsear_codigo,
    }


def test_repl_v2_sandbox_docker_no_usa_camino_normal(monkeypatch):
    command = repl_module.ReplCommandV2()
    entradas = iter(["imprimir(1)", "exit"])
    prevalidaciones: list[str] = []
    docker_calls: list[tuple[str, str]] = []
    normal_calls: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))
    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", lambda codigo: prevalidaciones.append(codigo))
    monkeypatch.setattr(
        command._delegate,
        "_ejecutar_en_docker",
        lambda codigo, backend: docker_calls.append((codigo, backend)),
    )
    monkeypatch.setattr(
        command,
        "_ejecutar_en_modo_normal",
        lambda codigo, _interpretador_cls: normal_calls.append(codigo),
    )

    args = _args_repl()
    args.sandbox_docker = "python"

    status = command.run(args)

    assert status == 0
    assert prevalidaciones == ["imprimir(1)"]
    assert docker_calls == [("imprimir(1)", "python")]
    assert normal_calls == []


def test_repl_v2_persistencia_estado_var_x_e_imprimir_x(monkeypatch, capsys):
    command = repl_module.ReplCommandV2()
    command._interpretador_persistente = {}
    entradas = iter(["var x = 10", "imprimir(x)", "exit"])
    estado: dict[str, int] = {}

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))
    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", lambda _codigo: [object()])
    monkeypatch.setattr(repl_module, "mostrar_info", lambda *_args, **_kwargs: None)

    def _fake_delegate(codigo: str):
        interpretador = command._delegate.interpretador or estado
        if codigo == "var x = 10":
            interpretador["x"] = 10
            command._delegate.interpretador = interpretador
            command._delegate._seguro_repl = False
            return
        assert codigo == "imprimir(x)"
        print(interpretador["x"])
        command._delegate.interpretador = interpretador
        command._delegate._seguro_repl = False

    monkeypatch.setattr(command._delegate, "ejecutar_codigo", _fake_delegate)

    status = command.run(_args_repl())

    assert status == 0
    assert capsys.readouterr().out == "10\n"


def test_repl_v2_bloque_anidado_real_mientras_si_fin_fin_acumula_hasta_completar(monkeypatch):
    command = repl_module.ReplCommandV2()
    entradas = iter(["mientras verdadero:", "si verdadero:", "fin", "fin", "exit"])
    parse_calls: list[str] = []
    ejecucion_calls: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    bloque_completo = "mientras verdadero:\nsi verdadero:\nfin\nfin"

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != bloque_completo:
            raise _parser_error_incompleto(TipoToken.FIN)
        return [object()]

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        command._delegate,
        "ejecutar_codigo",
        lambda codigo: ejecucion_calls.append(codigo),
    )

    status = command.run(_args_repl())

    assert status == 0
    assert parse_calls == [
        "mientras verdadero:",
        "mientras verdadero:\nsi verdadero:",
        "mientras verdadero:\nsi verdadero:\nfin",
        bloque_completo,
    ]
    assert ejecucion_calls == [bloque_completo]


def test_repl_v2_error_sintactico_real_limpia_buffer_y_repl_sigue(monkeypatch):
    command = repl_module.ReplCommandV2()
    entradas = iter(["si verdadero:", "imprimir(1", "var ok = 1", "exit"])
    parse_calls: list[str] = []
    ejecucion_calls: list[str] = []
    errores_reportados: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo == "si verdadero:":
            raise _parser_error_incompleto(TipoToken.FIN)
        if codigo == "si verdadero:\nimprimir(1":
            raise ParserError("Token inesperado: '('")
        return [object()]

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        command._delegate,
        "_log_error",
        lambda _categoria, err: errores_reportados.append(str(err)),
    )
    monkeypatch.setattr(
        command._delegate,
        "ejecutar_codigo",
        lambda codigo: ejecucion_calls.append(codigo),
    )

    status = command.run(_args_repl())

    assert status == 0
    assert parse_calls == ["si verdadero:", "si verdadero:\nimprimir(1", "var ok = 1"]
    assert ejecucion_calls == ["var ok = 1"]
    assert errores_reportados == ["Token inesperado: '('"]


def test_repl_v2_reset_estado_delegate_no_reinicia_interpretador():
    command = repl_module.ReplCommandV2()
    interpretador_inicial = command._delegate.interpretador

    command._reset_estado_delegate()

    assert command._delegate.interpretador is interpretador_inicial


def test_repl_v2_bloque_incompleto_no_ejecuta_ni_limpia_hasta_completar(monkeypatch):
    command = repl_module.ReplCommandV2()
    entradas = iter(["si verdadero:", "imprimir(1)", "fin", "exit"])
    parse_calls: list[str] = []
    ejecucion_calls: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    bloque_completo = "si verdadero:\nimprimir(1)\nfin"

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != bloque_completo:
            raise _parser_error_incompleto(TipoToken.FIN)
        return [object()]

    monkeypatch.setattr(repl_module, "prevalidar_y_parsear_codigo", _fake_parse)
    monkeypatch.setattr(
        command._delegate,
        "ejecutar_codigo",
        lambda codigo: ejecucion_calls.append(codigo),
    )

    status = command.run(_args_repl())

    assert status == 0
    assert parse_calls == ["si verdadero:", "si verdadero:\nimprimir(1)", bloque_completo]
    assert ejecucion_calls == [bloque_completo]
