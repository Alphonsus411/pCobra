import argparse

import pytest

from pcobra.cobra.cli.commands.compile_cmd import CompileCommand, LANG_CHOICES
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.target_policies import (
    ACCEPTED_TARGET_ALIASES,
    invalid_target_error,
    legacy_or_ambiguous_target_error,
    parse_target,
    parse_target_list,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.transpilers.registry import official_transpiler_targets

ACCEPTED_ALIASES = (
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


@pytest.mark.parametrize(("alias", "canonical"), ACCEPTED_ALIASES)
def test_parse_target_acepta_aliases_publicos(alias, canonical):
    assert parse_target(alias) == canonical


@pytest.mark.parametrize(("alias", "canonical"), ACCEPTED_ALIASES)
def test_parse_target_list_normaliza_aliases_en_mayusculas_y_minusculas(alias, canonical):
    assert parse_target_list(f"python,{alias}") == ["python", canonical]


@pytest.mark.parametrize("alias", REJECTED_ALIASES)
def test_parse_target_rechaza_aliases_no_permitidos(alias):
    with pytest.raises(argparse.ArgumentTypeError):
        parse_target(alias)


@pytest.mark.parametrize("legacy_name", ("js", "assembly", "nodejs", "python3"))
def test_parse_target_rechaza_nombres_legacy_o_ambiguos_con_error_explicito(legacy_name):
    with pytest.raises(argparse.ArgumentTypeError, match="legacy/ambiguo"):
        parse_target(legacy_name)
    assert "aliases UX públicos" in legacy_or_ambiguous_target_error(legacy_name)


def test_compile_parser_acepta_alias_c_mas_mas_y_entrega_canonico():
    parser = _build_parser_with_command(CompileCommand())
    args = parser.parse_args(["compilar", "script.co", "--tipo", "C++"])
    assert args.tipo == "cpp"


def test_compile_parser_acepta_alias_ensamblador_en_minusculas_y_entrega_canonico():
    parser = _build_parser_with_command(CompileCommand())
    args = parser.parse_args(["compilar", "script.co", "--tipo", "ensamblador"])
    assert args.tipo == "asm"


def test_transpilar_inverso_parser_acepta_alias_ensamblador_y_entrega_canonico(tmp_path):
    archivo = tmp_path / "script.py"
    archivo.write_text("print('ok')", encoding="utf-8")

    parser = _build_parser_with_command(TranspilarInversoCommand())
    args = parser.parse_args(
        [
            "transpilar-inverso",
            str(archivo),
            "--origen",
            "python",
            "--destino",
            "Ensamblador",
        ]
    )
    assert args.destino == "asm"


def test_transpilar_inverso_parser_acepta_alias_c_mas_mas_y_entrega_canonico(tmp_path):
    archivo = tmp_path / "script.py"
    archivo.write_text("print('ok')", encoding="utf-8")

    parser = _build_parser_with_command(TranspilarInversoCommand())
    args = parser.parse_args(
        [
            "transpilar-inverso",
            str(archivo),
            "--origen",
            "python",
            "--destino",
            "C++",
        ]
    )
    assert args.destino == "cpp"


def test_verify_parser_acepta_alias_c_mas_mas_y_normaliza_a_canonico():
    parser = _build_parser_with_command(VerifyCommand())
    args = parser.parse_args(["verificar", "script.co", "--lenguajes", "python,C++"])
    assert args.lenguajes == ["python", "cpp"]


def test_verify_parser_normaliza_alias_ensamblador_y_falla_por_runtime_restringido(caplog):
    parser = _build_parser_with_command(VerifyCommand())

    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "script.co", "--lenguajes", "python,Ensamblador"])

    assert "targets solo de transpilación asm" in caplog.text


def test_compile_parser_no_expone_aliases_en_choices_publicos():
    parser = _build_parser_with_command(CompileCommand())
    compile_parser = parser._subparsers._group_actions[0].choices["compilar"]

    tipo_action = next(action for action in compile_parser._actions if action.dest == "tipo")
    backend_action = next(action for action in compile_parser._actions if action.dest == "backend")

    assert tuple(tipo_action.choices) == tuple(LANG_CHOICES)
    assert tuple(backend_action.choices) == tuple(LANG_CHOICES)
    for alias, _ in ACCEPTED_ALIASES:
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


def test_la_whitelist_publica_sigue_canonica():
    targets = official_transpiler_targets()
    assert targets == tuple(LANG_CHOICES)
    assert targets == EXPECTED_CANONICAL_TARGETS
    assert len(targets) == 8
    assert len(set(targets)) == 8
    for alias, _ in ACCEPTED_ALIASES:
        assert alias not in targets


def test_aliases_publicos_no_amplian_el_set_canonico():
    assert tuple(ACCEPTED_TARGET_ALIASES) == (
        ("ensamblador", "asm"),
        ("c++", "cpp"),
    )

    for alias, canonical in ACCEPTED_TARGET_ALIASES:
        assert alias not in EXPECTED_CANONICAL_TARGETS
        assert canonical in EXPECTED_CANONICAL_TARGETS


def test_parse_target_rechaza_destino_fuera_del_set_canonico():
    with pytest.raises(argparse.ArgumentTypeError):
        parse_target("target_invalido")


def test_parse_target_list_rechaza_nombres_legacy_o_ambiguos():
    with pytest.raises(argparse.ArgumentTypeError, match="legacy/ambiguo"):
        parse_target_list("python,js")
