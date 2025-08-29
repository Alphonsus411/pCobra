import pytest
from argparse import Namespace

from cobra.cli.commands.execute_cmd import ExecuteCommand


def test_cli_ejecutar_archivo_inexistente(tmp_path):
    archivo = tmp_path / "no.co"
    cmd = ExecuteCommand()
    args = Namespace(archivo=str(archivo), sandbox=False, contenedor=None)
    with pytest.raises(FileNotFoundError) as exc:
        cmd.run(args)
    assert f"El archivo '{archivo}' no existe" in str(exc.value)
