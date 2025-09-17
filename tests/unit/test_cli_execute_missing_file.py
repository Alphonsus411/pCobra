from argparse import Namespace

from cobra.cli.commands.execute_cmd import ExecuteCommand
from cobra.cli.utils.messages import color_disabled


def test_cli_ejecutar_archivo_inexistente(tmp_path, capsys):
    archivo = tmp_path / "no.co"
    cmd = ExecuteCommand()
    args = Namespace(archivo=str(archivo), sandbox=False, contenedor=None)
    with color_disabled():
        codigo_salida = cmd.run(args)
    assert codigo_salida == 1
    salida = capsys.readouterr().out
    assert "No se encontró el archivo" in salida
    assert str(archivo) in salida
