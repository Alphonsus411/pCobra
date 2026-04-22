from argparse import _StoreAction

import pytest

from pcobra.cobra.cli.commands.compile_cmd import CompileCommand, get_lang_choices
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


def _build_parser():
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    cmd = CompileCommand()
    compile_parser = cmd.register_subparser(subparsers)
    return parser, compile_parser


def test_compile_tipo_choices_usa_lang_choices_centrales():
    _, compile_parser = _build_parser()
    action = next(
        a for a in compile_parser._actions if isinstance(a, _StoreAction) and a.dest == "tipo"
    )

    assert tuple(action.choices) == tuple(get_lang_choices())


def test_get_lang_choices_es_dinamico_tras_carga_de_entrypoints(monkeypatch):
    from pcobra.cobra.cli.commands import compile_cmd

    calls = {"ensure": 0}

    def _fake_ensure():
        calls["ensure"] += 1

    monkeypatch.setattr(compile_cmd, "cli_ensure_entrypoint_transpilers_loaded_once", _fake_ensure)
    monkeypatch.setattr(
        compile_cmd,
        "cli_transpiler_targets",
        lambda: ("python", "javascript", "rust", "wasm"),
    )

    assert get_lang_choices() == ("python", "javascript", "rust", "wasm")
    assert calls["ensure"] == 1


def test_compile_register_subparser_evalua_choices_en_tiempo_de_registro(monkeypatch):
    from pcobra.cobra.cli.commands import compile_cmd

    monkeypatch.setattr(compile_cmd, "get_lang_choices", lambda: ("python", "rust"))
    monkeypatch.setattr(compile_cmd, "enabled_internal_legacy_targets", lambda: ())

    _, compile_parser = _build_parser()
    action = next(
        a for a in compile_parser._actions if isinstance(a, _StoreAction) and a.dest == "tipo"
    )

    assert tuple(action.choices) == ("python", "rust")


def test_compile_parser_normaliza_targets_canonicos_en_tipo_y_tipos():
    parser, _ = _build_parser()

    args = parser.parse_args(["compilar", "input.co", "--tipo", "rust", "--tipos", "python,javascript,rust"])

    assert args.tipo == "rust"
    assert args.tipos == ["python", "javascript", "rust"]


def test_compile_parser_backend_rechaza_alias_legacy_explicito():
    parser, _ = _build_parser()
    legacy_js = "j" "s"

    with pytest.raises(SystemExit):
        parser.parse_args(["compilar", "input.co", "--backend", legacy_js])


def test_compile_parser_tipos_rechaza_alias_legacy_explicito():
    parser, _ = _build_parser()
    legacy_assembly = "as" "sembly"

    with pytest.raises(SystemExit):
        parser.parse_args(["compilar", "input.co", "--tipos", f"python,{legacy_assembly}"])


def test_compile_help_refleja_solo_nombres_canonicos():
    _, compile_parser = _build_parser()
    help_text = compile_parser.format_help()

    normalized_help = " ".join(help_text.split())

    assert "Tier 1: python, javascript, rust." in normalized_help
    assert "Tier 2:" not in normalized_help
    assert "JavaScript (javascript)" not in help_text
    assert "Ensamblador (asm)" not in help_text
    for target in OFFICIAL_TARGETS:
        assert target in help_text
