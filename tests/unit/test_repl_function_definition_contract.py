from io import StringIO
from unittest.mock import patch

from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.core.runtime import InterpretadorCobra


def test_repl_definir_funcion_no_ejecuta_cuerpo_ni_postprocesa_echo() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())

    codigo_def = """
func hola():
    imprimir('EJECUTADO')
fin
"""

    with patch("sys.stdout", new_callable=StringIO) as out:
        cmd.ejecutar_codigo(codigo_def)
    assert out.getvalue() == ""

    with patch("sys.stdout", new_callable=StringIO) as out:
        cmd.ejecutar_codigo("hola()")
    assert out.getvalue().splitlines()[-1] == "EJECUTADO"


def test_definir_funcion_no_ejecuta_cuerpo_en_repl() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())

    codigo_def = """
func doble(y):
    retorno y + y
fin
func triple(x):
    retorno doble(x) + x
fin
"""

    with patch("sys.stdout", new_callable=StringIO) as out:
        cmd.ejecutar_codigo(codigo_def)

    salida = out.getvalue()
    assert "WARNING: Llamada a funcion: doble" not in salida
    assert "Variable no declarada: x" not in salida

    simbolo_triple = None
    if hasattr(cmd.interpretador, "contextos") and cmd.interpretador.contextos:
        simbolo_triple = cmd.interpretador.contextos[-1].get("triple")
    if simbolo_triple is None and hasattr(cmd.interpretador, "variables"):
        simbolo_triple = cmd.interpretador.variables.get("triple")

    assert simbolo_triple is not None


def _capturar_repl(cmd: InteractiveCommand, codigo: str) -> tuple[str, list[str]]:
    import logging

    logger = logging.getLogger()
    prev_handlers = list(logger.handlers)
    prev_level = logger.level
    stream_logs = StringIO()
    logger.handlers = [logging.StreamHandler(stream_logs)]
    logger.setLevel(logging.WARNING)
    try:
        with patch("sys.stdout", new_callable=StringIO) as out:
            cmd.ejecutar_codigo(codigo)
        return out.getvalue(), [ln.strip() for ln in stream_logs.getvalue().splitlines() if ln.strip()]
    finally:
        logger.handlers = prev_handlers
        logger.setLevel(prev_level)


def test_repl_warning_llamada_funcion_simple_conteo_unico_y_resultado_visible() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())
    _capturar_repl(cmd, """
func test(x):
    retorno x
fin
""")
    salida_stdout, salida_logging = _capturar_repl(cmd, "test(1)")

    assert salida_stdout.splitlines().count("WARNING: Llamada a funcion: test") == 1
    assert "1" in salida_stdout
    assert not any("WARNING: Llamada a funcion: test" in ln for ln in salida_logging)


def test_repl_warning_llamada_funcion_anidada_orden_cardinalidad_y_resultado() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())
    _capturar_repl(cmd, """
func doble(x):
    retorno x + x
fin
func triple(x):
    retorno doble(x) + x
fin
""")
    salida_stdout, salida_logging = _capturar_repl(cmd, "triple(3)")

    warnings = [ln for ln in salida_stdout.splitlines() if ln.startswith("WARNING: Llamada a funcion:")]
    assert warnings.count("WARNING: Llamada a funcion: triple") == 1
    assert warnings.count("WARNING: Llamada a funcion: doble") == 1
    assert warnings.index("WARNING: Llamada a funcion: triple") < warnings.index("WARNING: Llamada a funcion: doble")
    assert "9" in salida_stdout
    assert not any("WARNING: Llamada a funcion: triple" in ln for ln in salida_logging)
    assert not any("WARNING: Llamada a funcion: doble" in ln for ln in salida_logging)
