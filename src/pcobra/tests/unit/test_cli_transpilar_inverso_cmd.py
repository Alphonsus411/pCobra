import argparse
from io import StringIO
from unittest.mock import patch

from cobra.cli.cli import main
from cobra.cli.utils import messages


class FakeReverse:
    def load_file(self, path):
        return []


class FakeTranspiler:
    def generate_code(self, ast):
        return "resultado"


def test_transpilar_inverso_ok(tmp_path):
    archivo = tmp_path / "a.py"
    archivo.write_text("x = 1")
    args = ["--no-color", "transpilar-inverso", str(archivo), "--origen=python", "--destino=python"]
    with patch("cli.commands.transpilar_inverso_cmd.REVERSE_TRANSPILERS", {"python": FakeReverse}), \
         patch("cli.commands.transpilar_inverso_cmd.TRANSPILERS", {"python": FakeTranspiler}), \
         patch("sys.stdout", new_callable=StringIO) as out:
        main(args)
    lineas = [l for l in out.getvalue().splitlines() if "Código transpilado" in l]
    assert lineas[0].startswith("Código transpilado")
    assert out.getvalue().strip().splitlines()[-1] == "resultado"


def test_transpilar_inverso_archivo_inexistente(tmp_path):
    archivo = tmp_path / "no.py"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["transpilar-inverso", str(archivo)])
    assert f"El archivo '{archivo}' no existe" in out.getvalue()
