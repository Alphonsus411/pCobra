import logging
from contextlib import redirect_stderr
from io import StringIO
from types import SimpleNamespace

from pcobra.cli import configure_logging
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand


def _run_interactive_and_capture_debug_traces(debug: bool) -> str:
    configure_logging(debug=debug)
    cmd = InteractiveCommand(SimpleNamespace(ejecutar_ast=lambda ast: None))
    cmd.procesar_ast = lambda codigo, validador=None: []  # type: ignore[assignment]
    buffer = StringIO()
    root_logger = logging.getLogger()
    original_streams = []
    for handler in root_logger.handlers:
        if hasattr(handler, "stream"):
            original_streams.append((handler, handler.stream))
            handler.setStream(buffer)
    with redirect_stderr(buffer):
        cmd.ejecutar_codigo("imprimir(1)")
    for handler, stream in original_streams:
        handler.setStream(stream)
    return buffer.getvalue()


def test_sin_debug_no_aparecen_trazas_internas():
    salida = _run_interactive_and_capture_debug_traces(debug=False)
    assert "[RUN]" not in salida
    assert "[EXEC]" not in salida
    assert "[EVAL]" not in salida


def test_con_debug_si_aparecen_trazas_internas():
    salida = _run_interactive_and_capture_debug_traces(debug=True)
    assert "[RUN] Ejecutando snippet en REPL" in salida
    assert "[EXEC] Ejecutando AST en intérprete" in salida
    assert "[EVAL] Resultado de evaluación" in salida


def test_configure_logging_es_idempotente_y_no_duplica_emision():
    configure_logging(debug=True)
    configure_logging(debug=True)

    root_logger = logging.getLogger()
    assert len(root_logger.handlers) == 1

    buffer = StringIO()
    original_stream = None
    handler = root_logger.handlers[0]
    if hasattr(handler, "stream"):
        original_stream = handler.stream
        handler.setStream(buffer)

    try:
        logging.getLogger("pcobra.test").debug("mensaje único")
    finally:
        if original_stream is not None:
            handler.setStream(original_stream)

    salida = buffer.getvalue()
    assert salida.count("mensaje único") == 1
