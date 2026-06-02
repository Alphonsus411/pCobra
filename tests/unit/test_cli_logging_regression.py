import logging
from contextlib import redirect_stderr
from io import StringIO
from types import SimpleNamespace

from pcobra.cli import configure_logging, ensure_sqlite_db_key_for_command
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand


def _run_interactive_and_capture_debug_traces(debug: bool) -> str:
    configure_logging(debug=debug)
    cmd = InteractiveCommand(SimpleNamespace(ejecutar_ast=lambda ast: None, ejecutar_nodo=lambda nodo: None))
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


def test_configure_logging_no_duplica_debug_ni_error_en_consola():
    configure_logging(debug=True)
    configure_logging(debug=True)

    root_logger = logging.getLogger()
    assert len(root_logger.handlers) == 1

    buffer = StringIO()
    handler = root_logger.handlers[0]
    original_stream = getattr(handler, "stream", None)
    if hasattr(handler, "setStream"):
        handler.setStream(buffer)

    try:
        logger = logging.getLogger("pcobra.test")
        logger.debug("debug sin duplicación")
        logger.error("error sin duplicación")
    finally:
        if original_stream is not None and hasattr(handler, "setStream"):
            handler.setStream(original_stream)

    salida = buffer.getvalue()
    assert salida.count("debug sin duplicación") == 1
    assert salida.count("error sin duplicación") == 1


def test_configure_logging_pcobra_sin_handlers_locales_y_con_propagacion():
    configure_logging(debug=False)
    app_logger = logging.getLogger("pcobra")

    assert app_logger.handlers == []
    assert app_logger.propagate is True


def _capturar_mensajes_diagnosticos(*, debug: bool, verbose: int = 0) -> str:
    configure_logging(debug=debug, verbose=verbose)
    buffer = StringIO()
    root_logger = logging.getLogger()
    handler = root_logger.handlers[0]
    original_stream = getattr(handler, "stream", None)
    if hasattr(handler, "setStream"):
        handler.setStream(buffer)
    try:
        logging.warning("Llamada a funcion: demo")
        logging.warning("Usar modulo: demo")
        logging.warning("USAR sanitize conflicts event module=demo count=1")
    finally:
        if original_stream is not None and hasattr(handler, "setStream"):
            handler.setStream(original_stream)
    return buffer.getvalue()


def test_modo_normal_oculta_warnings_diagnosticos():
    salida = _capturar_mensajes_diagnosticos(debug=False, verbose=0)
    assert "Llamada a funcion: demo" not in salida
    assert "Usar modulo: demo" not in salida
    assert "USAR sanitize conflicts event module=demo" not in salida


def test_modo_debug_muestra_warnings_diagnosticos():
    salida = _capturar_mensajes_diagnosticos(debug=True, verbose=0)
    assert "Llamada a funcion: demo" in salida
    assert "Usar modulo: demo" in salida
    assert "USAR sanitize conflicts event module=demo" in salida


def test_modo_verbose_muestra_warnings_diagnosticos():
    salida = _capturar_mensajes_diagnosticos(debug=False, verbose=1)
    assert "Llamada a funcion: demo" in salida
    assert "Usar modulo: demo" in salida
    assert "USAR sanitize conflicts event module=demo" in salida


def _capturar_warning_seguridad(*, debug: bool, verbose: int = 0) -> str:
    configure_logging(debug=debug, verbose=verbose)
    buffer = StringIO()
    root_logger = logging.getLogger()
    handler = root_logger.handlers[0]
    original_stream = getattr(handler, "stream", None)
    if hasattr(handler, "setStream"):
        handler.setStream(buffer)
    try:
        ensure_sqlite_db_key_for_command(
            command_name="cache",
            dev_ephemeral_cli_confirmation=True,
        )
    finally:
        if original_stream is not None and hasattr(handler, "setStream"):
            handler.setStream(original_stream)
    return buffer.getvalue()


def test_modo_normal_preserva_warnings_seguridad_runtime(monkeypatch):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setenv("COBRA_DEV_MODE", "1")
    monkeypatch.setenv("COBRA_DEV_ALLOW_EPHEMERAL_KEY", "1")

    salida = _capturar_warning_seguridad(debug=False, verbose=0)
    assert "Modo desarrollo confirmado" in salida
    assert "SQLITE_DB_KEY" in salida


def test_modo_normal_preserva_warnings_funcionales_no_diagnosticos():
    configure_logging(debug=False, verbose=0)
    buffer = StringIO()
    root_logger = logging.getLogger()
    handler = root_logger.handlers[0]
    original_stream = getattr(handler, "stream", None)
    if hasattr(handler, "setStream"):
        handler.setStream(buffer)
    try:
        logging.getLogger("pcobra.test").warning("Aviso funcional importante")
    finally:
        if original_stream is not None and hasattr(handler, "setStream"):
            handler.setStream(original_stream)

    assert "Aviso funcional importante" in buffer.getvalue()
