import argparse
from io import StringIO
from unittest.mock import patch

from cobra.cli.cli import main


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
    with patch("pcobra.cobra.cli.commands.transpilar_inverso_cmd.REVERSE_TRANSPILERS", {"python": FakeReverse}), \
         patch("pcobra.cobra.cli.commands.transpilar_inverso_cmd.TRANSPILERS", {"python": FakeTranspiler}), \
         patch("sys.stdout", new_callable=StringIO) as out:
        main(args)
    lineas = [l for l in out.getvalue().splitlines() if "Código transpilado" in l]
    assert lineas[0].startswith("Código transpilado")
    assert out.getvalue().strip().splitlines()[-1] == "resultado"


def test_transpilar_inverso_archivo_inexistente(tmp_path):
    archivo = tmp_path / "no.py"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main([
            "transpilar-inverso",
            str(archivo),
            "--origen=python",
            "--destino=python",
        ])
    assert f"El archivo '{archivo}' no existe" in out.getvalue()


def test_transpilar_inverso_consistencia_registry_cli():
    from pcobra.cobra.cli.commands import transpilar_inverso_cmd

    transpilar_inverso_cmd.validar_consistencia_reverse_transpilers()
    policy = set(transpilar_inverso_cmd.reverse_module.REVERSE_SCOPE_LANGUAGES)
    assert set(transpilar_inverso_cmd.REVERSE_TRANSPILERS.keys()).issubset(policy)
    assert set(transpilar_inverso_cmd.REVERSE_TRANSPILERS.keys()) == set(transpilar_inverso_cmd.ORIGIN_CHOICES)
