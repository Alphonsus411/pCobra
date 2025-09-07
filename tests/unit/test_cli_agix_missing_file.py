import pytest
from argparse import Namespace

from cobra.cli.commands.agix_cmd import AgixCommand


def test_cli_agix_archivo_inexistente(tmp_path):
    archivo = tmp_path / "no.co"
    cmd = AgixCommand()
    args = Namespace(
        archivo=str(archivo),
        peso_precision=None,
        peso_interpretabilidad=None,
        placer=None,
        activacion=None,
        dominancia=None,
    )
    with pytest.raises(FileNotFoundError) as exc:
        cmd.run(args)
    assert f"El archivo '{archivo}' no existe" in str(exc.value)
