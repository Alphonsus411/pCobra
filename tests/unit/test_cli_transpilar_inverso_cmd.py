import argparse
from io import StringIO
from unittest.mock import patch

import pytest

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
    assert set(transpilar_inverso_cmd.ORIGIN_CHOICES) == policy


def test_transpilar_inverso_origen_fuera_de_politica(tmp_path):
    from pcobra.cobra.cli.commands import transpilar_inverso_cmd

    archivo = tmp_path / "a.rs"
    archivo.write_text("fn main() {}")

    parser = transpilar_inverso_cmd.CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    transpilar_inverso_cmd.TranspilarInversoCommand().register_subparser(subparsers)

    with pytest.raises(SystemExit):
        parser.parse_args([
            "transpilar-inverso",
            str(archivo),
            "--origen=rust",
            "--destino=python",
        ])


def test_transpilar_inverso_destino_fuera_tier_rechazado_explicitamente():
    from pcobra.cobra.cli.commands import transpilar_inverso_cmd

    cmd = transpilar_inverso_cmd.TranspilarInversoCommand()

    with patch.object(transpilar_inverso_cmd, "TRANSPILERS", {"python": FakeTranspiler, "externo": FakeTranspiler}):
        try:
            cmd._verificar_dependencias("python", "externo")
        except transpilar_inverso_cmd.UnsupportedLanguageError as exc:
            mensaje = str(exc)
        else:
            raise AssertionError("Se esperaba UnsupportedLanguageError para destino externo")

    assert "fuera de Tier 1/Tier 2" in mensaje
    assert "externo" in mensaje


def test_transpilar_inverso_acepta_origen_canonico_javascript(tmp_path):
    from pcobra.cobra.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand
    from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser

    archivo = tmp_path / "a.py"
    archivo.write_text("x = 1")

    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    TranspilarInversoCommand().register_subparser(subparsers)

    args = parser.parse_args([
        "transpilar-inverso",
        str(archivo),
        "--origen=javascript",
        "--destino=python",
    ])

    assert args.origen == "javascript"


def test_transpilar_inverso_ayuda_acota_origen_y_targets_oficiales():
    from pcobra.cobra.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand
    from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser

    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    subparser = TranspilarInversoCommand().register_subparser(subparsers)

    ayuda = subparser.format_help()

    assert "reverse transpilation" in ayuda.lower()
    assert "official_targets" in ayuda.lower()


def test_parse_reverse_source_language_rechaza_alias_legacy():
    from pcobra.cobra.transpilers.reverse.policy import parse_reverse_source_language

    with pytest.raises(argparse.ArgumentTypeError):
        parse_reverse_source_language("js")
