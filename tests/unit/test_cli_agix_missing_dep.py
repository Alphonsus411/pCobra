from argparse import Namespace
from unittest.mock import patch

from cobra.cli.commands.agix_cmd import AgixCommand
from pcobra.ia.analizador_agix import DependenciaAGIXNoDisponibleError


def test_cli_agix_sin_agix(tmp_path, capsys):
    archivo = tmp_path / "ejemplo.cobra"
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
    assert "dependencia oficial 'agix'" in salida
    assert "pip install agix" in salida


def test_cli_agix_captura_solo_excepcion_especifica_de_dependencia(tmp_path, capsys):
    archivo = tmp_path / "ejemplo.cobra"
    archivo.write_text("var x = 5")
    args = Namespace(
        archivo=str(archivo),
        peso_precision=None,
        peso_interpretabilidad=None,
        placer=None,
        activacion=None,
        dominancia=None,
    )
    with patch(
        "pcobra.cobra.cli.commands.agix_cmd.generar_sugerencias",
        side_effect=DependenciaAGIXNoDisponibleError("instala AGIX"),
    ):
        exit_code = AgixCommand().run(args)

    assert exit_code == 1
    assert "AGIX no está disponible: instala AGIX" in capsys.readouterr().out
