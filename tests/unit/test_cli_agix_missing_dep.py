from argparse import Namespace
from unittest.mock import patch

from cobra.cli.commands.agix_cmd import AgixCommand


def test_cli_agix_sin_agix(tmp_path, capsys):
    archivo = tmp_path / "ejemplo.co"
    archivo.write_text("var x = 5")
    cmd = AgixCommand()
    args = Namespace(
        archivo=str(archivo),
        peso_precision=None,
        peso_interpretabilidad=None,
        placer=None,
        activacion=None,
        dominancia=None,
    )
    with patch("pcobra.ia.analizador_agix.Reasoner", None):
        exit_code = cmd.run(args)
    salida = capsys.readouterr().out
    assert exit_code == 1
    assert "Instala el paquete agix" in salida
