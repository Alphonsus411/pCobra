import argparse

from pcobra.cobra.cli.commands_v2 import repl_cmd as repl_module
from pcobra.cobra.core import ParserError

ReplCommandV2 = repl_module.ReplCommandV2

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
            raise ParserError("Se esperaba 'fin' para cerrar el bloque condicional")
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


def test_repl_v2_no_sale_con_exit_si_hay_bloque_pendiente(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["si verdadero:", "exit", "fin", "exit"])
    parse_calls: list[str] = []
    pipeline_calls: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != "si verdadero:\nexit\nfin":
            raise ParserError("Se esperaba 'fin' para cerrar el bloque condicional")
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
    assert parse_calls == ["si verdadero:", "si verdadero:\nexit", "si verdadero:\nexit\nfin"]
    assert pipeline_calls == ["si verdadero:\nexit\nfin"]


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
            raise ParserError("Se esperaba 'fin' para cerrar el bloque condicional")
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


def test_repl_v2_error_ejecucion_limpia_buffer_actual_y_continua(monkeypatch):
    command = ReplCommandV2()
    entradas = iter(["si verdadero:", "fin", "var z = 9", "exit"])
    pipeline_calls: list[str] = []
    logged: list[str] = []

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        if codigo == "si verdadero:":
            raise ParserError("Se esperaba 'fin' para cerrar el bloque condicional")
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


def test_repl_v2_soporta_bloque_anidado_con_fin(monkeypatch):
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
    estado: dict[str, int] = {}

    monkeypatch.setattr("builtins.input", lambda _prompt: next(entradas))

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo not in {
            "mientras verdadero:\nsi verdadero:\nvar total = 5\nromper\nfin\nfin",
            "imprimir(total)",
        }:
            raise ParserError("Se esperaba 'fin' para cerrar el bloque condicional")
        return []

    class _Setup:
        def __init__(self, interpretador):
            self.interpretador = interpretador
            self.safe_mode = False
            self.validadores_extra = None

    def _fake_pipeline(pipeline_input, **_kwargs):
        pipeline_calls.append(pipeline_input.codigo)
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
    assert parse_calls[-2:] == [
        "mientras verdadero:\nsi verdadero:\nvar total = 5\nromper\nfin\nfin",
        "imprimir(total)",
    ]
    assert pipeline_calls == [
        "mientras verdadero:\nsi verdadero:\nvar total = 5\nromper\nfin\nfin",
        "imprimir(total)",
    ]
