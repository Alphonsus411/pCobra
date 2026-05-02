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
    assert out.getvalue().strip() == "EJECUTADO"


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
