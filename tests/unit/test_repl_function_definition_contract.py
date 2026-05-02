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
