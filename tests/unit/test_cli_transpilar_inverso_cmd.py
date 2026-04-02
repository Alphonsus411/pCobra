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

class FakeReverseWithUnsupportedNode:
    def load_file(self, path):
        return []

    def generate_ast(self, code):
        raise NotImplementedError("Nodo no soportado: import_statement")


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
    assert "resultado" in out.getvalue()


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
    assert tuple(transpilar_inverso_cmd.ORIGIN_CHOICES) == (
        "python",
        "javascript",
        "java",
    )


def test_regresion_transpilar_inverso_rechaza_origen_reverse_retirado_rust(tmp_path):
    from pcobra.cobra.cli.commands import transpilar_inverso_cmd

    # Regresión: `rust` ya no forma parte de los orígenes reverse oficiales;
    # este caso conserva el rechazo explícito, no un soporte vigente.
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
        except (transpilar_inverso_cmd.UnsupportedLanguageError, argparse.ArgumentTypeError) as exc:
            mensaje = str(exc)
        else:
            raise AssertionError("Se esperaba UnsupportedLanguageError para destino externo")

    assert "soportado" in mensaje or "fuera de Tier 1/Tier 2" in mensaje
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

    ayuda_normalizada = ayuda.lower()
    assert "orígenes reverse" in ayuda_normalizada or "origen" in ayuda_normalizada
    assert "tier 1" in ayuda_normalizada
    assert "tier 2" in ayuda_normalizada


def test_regresion_parse_reverse_source_language_rechaza_valor_fuera_del_scope():
    from pcobra.cobra.transpilers.reverse.policy import parse_reverse_source_language

    with pytest.raises(argparse.ArgumentTypeError):
        parse_reverse_source_language("fantasy")


def test_regresion_transpilar_inverso_choices_y_scope_siguen_alineados_con_politica():
    from pcobra.cobra.cli.commands import transpilar_inverso_cmd

    assert transpilar_inverso_cmd.ORIGIN_CHOICES == ("python", "javascript", "java")
    assert transpilar_inverso_cmd.reverse_module.REVERSE_SCOPE_LANGUAGES == (
        "python",
        "javascript",
        "java",
    )
    assert set(transpilar_inverso_cmd.REVERSE_TRANSPILERS) == {
        "python",
        "javascript",
        "java",
    }


def test_transpilar_inverso_reporta_cuando_no_hay_reverse_para_destino(tmp_path):
    archivo = tmp_path / "a.py"
    archivo.write_text("x = 1")
    args = [
        "--no-color",
        "transpilar-inverso",
        str(archivo),
        "--origen=python",
        "--destino=rust",
    ]
    with patch("pcobra.cobra.cli.commands.transpilar_inverso_cmd.REVERSE_TRANSPILERS", {"python": FakeReverse}), \
         patch("pcobra.cobra.cli.commands.transpilar_inverso_cmd.TRANSPILERS", {"rust": FakeTranspiler}), \
         patch("sys.stdout", new_callable=StringIO) as out:
        main(args)

    salida = out.getvalue()
    assert "No hay parser inverso para destino 'rust'" in salida


def test_transpilar_inverso_reporta_degradacion_por_nodo_no_soportado(tmp_path):
    archivo = tmp_path / "a.py"
    archivo.write_text("x = 1")
    args = [
        "--no-color",
        "transpilar-inverso",
        str(archivo),
        "--origen=python",
        "--destino=python",
    ]
    with patch(
        "pcobra.cobra.cli.commands.transpilar_inverso_cmd.REVERSE_TRANSPILERS",
        {"python": FakeReverseWithUnsupportedNode},
    ), patch(
        "pcobra.cobra.cli.commands.transpilar_inverso_cmd.TRANSPILERS",
        {"python": FakeTranspiler},
    ), patch("sys.stdout", new_callable=StringIO) as out:
        main(args)

    salida = out.getvalue()
    assert "Conversión parcial detectada" in salida
