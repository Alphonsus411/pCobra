import argparse

import pytest

from pcobra.cobra.cli.commands.compile_cmd import CompileCommand, LANG_CHOICES
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.target_policies import invalid_target_error, parse_target, parse_target_list
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.transpilers.registry import official_transpiler_targets

ACCEPTED_ALIASES = (
    ("c++", "cpp"),
    ("ensamblador", "asm"),
    ("C++", "cpp"),
    ("Ensamblador", "asm"),
)

REJECTED_ALIASES = ("js", "assembly")


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


def test_help_y_error_muestran_canones_y_ejemplos_de_alias():
    parser = _build_parser_with_command(CompileCommand())
    compile_parser = parser._subparsers._group_actions[0].choices["compilar"]
    help_text = compile_parser.format_help().lower()

    assert "python" in help_text
    assert "rust" in help_text
    assert "javascript" in help_text
    assert "wasm" in help_text
    assert "go" in help_text
    assert "cpp" in help_text
    assert "java" in help_text
    assert "asm" in help_text
    assert "aliases aceptados:" in help_text
    assert "c++→cpp" in help_text
    assert "ensamblador→asm" in help_text

    message = invalid_target_error("desconocido")
    assert "python, rust, javascript, wasm, go, cpp, java, asm" in message
    assert "Aliases aceptados:" in message
    assert "c++→cpp" in message
    assert "ensamblador→asm" in message


def test_la_whitelist_publica_sigue_canonica():
    targets = official_transpiler_targets()
    assert targets == tuple(LANG_CHOICES)
    assert targets == ("python", "rust", "javascript", "wasm", "go", "cpp", "java", "asm")
    assert len(targets) == 8
    for alias, _ in ACCEPTED_ALIASES:
        assert alias not in targets
