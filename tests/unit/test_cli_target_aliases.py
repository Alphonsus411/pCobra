import argparse
import pytest

from pcobra.cobra.cli.commands.compile_cmd import CompileCommand, LANG_CHOICES
from pcobra.cobra.cli.commands.benchmarks_cmd import BenchmarksCommand
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.target_policies import (
    ACCEPTED_TARGET_ALIASES,
    accepted_target_aliases_examples_text,
    invalid_target_error,
    legacy_or_ambiguous_target_error,
    parse_target,
    parse_target_list,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.transpilers.registry import official_transpiler_targets
from scripts.targets_policy_common import PUBLIC_TEXT_PATHS, find_public_alias_errors

LEGACY_AMBIGUOUS_ALIASES = (
    ("c++", "cpp"),
    ("ensamblador", "asm"),
    ("C++", "cpp"),
    ("Ensamblador", "asm"),
)

REJECTED_ALIASES = ("js", "assembly")
EXPECTED_CANONICAL_TARGETS = (
    "python",
    "rust",
    "javascript",
    "wasm",
    "go",
    "cpp",
    "java",
    "asm",
)


def _build_parser_with_command(command):
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    command.register_subparser(subparsers)
    return parser


@pytest.mark.parametrize(("alias", "_canonical"), LEGACY_AMBIGUOUS_ALIASES)
def test_parse_target_rechaza_aliases_legacy_o_ambiguos(alias, _canonical):
    with pytest.raises(argparse.ArgumentTypeError, match="legacy/ambiguo"):
        parse_target(alias)


@pytest.mark.parametrize(("alias", "_canonical"), LEGACY_AMBIGUOUS_ALIASES)
def test_parse_target_list_rechaza_aliases_legacy_o_ambiguos(alias, _canonical):
    with pytest.raises(argparse.ArgumentTypeError, match="legacy/ambiguo"):
        parse_target_list(f"python,{alias}")


@pytest.mark.parametrize("alias", REJECTED_ALIASES)
def test_parse_target_rechaza_aliases_no_permitidos(alias):
    with pytest.raises(argparse.ArgumentTypeError):
        parse_target(alias)


@pytest.mark.parametrize("legacy_name", ("js", "assembly", "nodejs", "python3"))
def test_parse_target_rechaza_nombres_legacy_o_ambiguos_con_error_explicito(legacy_name):
    with pytest.raises(argparse.ArgumentTypeError, match="legacy/ambiguo"):
        parse_target(legacy_name)
    assert "nombres canónicos oficiales" in legacy_or_ambiguous_target_error(legacy_name)


def test_compile_parser_rechaza_alias_c_mas_mas():
    parser = _build_parser_with_command(CompileCommand())
    with pytest.raises(SystemExit):
        parser.parse_args(["compilar", "script.co", "--tipo", "C++"])


def test_compile_parser_rechaza_alias_ensamblador_en_minusculas():
    parser = _build_parser_with_command(CompileCommand())
    with pytest.raises(SystemExit):
        parser.parse_args(["compilar", "script.co", "--tipo", "ensamblador"])


def test_transpilar_inverso_parser_rechaza_alias_ensamblador(tmp_path):
    archivo = tmp_path / "script.py"
    archivo.write_text("print('ok')", encoding="utf-8")

    parser = _build_parser_with_command(TranspilarInversoCommand())
    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "transpilar-inverso",
                str(archivo),
                "--origen",
                "python",
                "--destino",
                "Ensamblador",
            ]
        )


def test_transpilar_inverso_parser_rechaza_alias_c_mas_mas(tmp_path):
    archivo = tmp_path / "script.py"
    archivo.write_text("print('ok')", encoding="utf-8")

    parser = _build_parser_with_command(TranspilarInversoCommand())
    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "transpilar-inverso",
                str(archivo),
                "--origen",
                "python",
                "--destino",
                "C++",
            ]
        )


def test_verify_parser_rechaza_alias_c_mas_mas():
    parser = _build_parser_with_command(VerifyCommand())
    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "script.co", "--lenguajes", "python,C++"])


def test_verify_parser_rechaza_alias_ensamblador():
    parser = _build_parser_with_command(VerifyCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "script.co", "--lenguajes", "python,Ensamblador"])


def test_compile_parser_no_expone_aliases_en_choices_publicos():
    parser = _build_parser_with_command(CompileCommand())
    compile_parser = parser._subparsers._group_actions[0].choices["compilar"]

    tipo_action = next(action for action in compile_parser._actions if action.dest == "tipo")
    backend_action = next(action for action in compile_parser._actions if action.dest == "backend")

    assert tuple(tipo_action.choices) == tuple(LANG_CHOICES)
    assert tuple(backend_action.choices) == tuple(LANG_CHOICES)
    for alias, _ in LEGACY_AMBIGUOUS_ALIASES:
        assert alias not in tipo_action.choices
        assert alias not in backend_action.choices


def test_help_y_error_muestran_solo_nombres_canonicos_oficiales():
    parser = _build_parser_with_command(CompileCommand())
    compile_parser = parser._subparsers._group_actions[0].choices["compilar"]
    help_text = compile_parser.format_help().lower()

    for target in EXPECTED_CANONICAL_TARGETS:
        assert target in help_text

    message = invalid_target_error("desconocido")
    assert ", ".join(EXPECTED_CANONICAL_TARGETS) in message


@pytest.mark.parametrize(
    ("surface_name", "command"),
    (
        ("compile", CompileCommand()),
        ("verify", VerifyCommand()),
        ("reverse", TranspilarInversoCommand()),
        ("benchmarks", BenchmarksCommand()),
    ),
)
def test_help_publico_de_comandos_no_reintroduce_aliases_legacy(surface_name, command):
    parser = _build_parser_with_command(command)
    help_text = parser.format_help().lower()
    for alias in REJECTED_ALIASES:
        assert alias not in help_text, f"{surface_name} help expone alias '{alias}'"


def test_docs_publicas_activas_no_exponen_aliases_legacy():
    monitored = (
        "README.md",
        "docs/targets_policy.md",
        "docs/matriz_transpiladores.md",
        "docs/frontend/cli.rst",
    )
    for path in PUBLIC_TEXT_PATHS:
        rel = path.relative_to(path.cwd()).as_posix()
        if rel not in monitored:
            continue
        content = path.read_text(encoding="utf-8")
        assert not find_public_alias_errors(rel, content), (
            f"{rel} expone aliases legacy en una superficie pública activa"
        )


def test_error_legacy_publico_no_reintroduce_aliases_en_texto():
    error_text = legacy_or_ambiguous_target_error("js").lower()
    canonical_section = error_text.split(":", maxsplit=2)[-1]

    for target in EXPECTED_CANONICAL_TARGETS:
        assert target in error_text

    for forbidden_token in (*REJECTED_ALIASES, *(alias.lower() for alias, _ in LEGACY_AMBIGUOUS_ALIASES)):
        assert forbidden_token not in canonical_section


def test_la_whitelist_publica_sigue_canonica():
    targets = official_transpiler_targets()
    assert targets == tuple(LANG_CHOICES)
    assert targets == EXPECTED_CANONICAL_TARGETS
    assert len(targets) == 8
    assert len(set(targets)) == 8
    for alias, _ in LEGACY_AMBIGUOUS_ALIASES:
        assert alias not in targets


def test_aliases_publicos_se_mantienen_vacios():
    assert tuple(ACCEPTED_TARGET_ALIASES) == ()
    assert accepted_target_aliases_examples_text() == "sin aliases públicos"


def test_parse_target_rechaza_destino_fuera_del_set_canonico():
    with pytest.raises(argparse.ArgumentTypeError):
        parse_target("target_invalido")


def test_parse_target_list_rechaza_nombres_legacy_o_ambiguos():
    with pytest.raises(argparse.ArgumentTypeError, match="legacy/ambiguo"):
        parse_target_list("python,js")
