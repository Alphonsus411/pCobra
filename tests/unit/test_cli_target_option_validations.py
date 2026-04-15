from types import SimpleNamespace

import pytest

from pcobra.cobra.cli.commands.benchmarks_cmd import BACKENDS, BenchmarksCommand
from pcobra.cobra.cli.commands.compile_cmd import CompileCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.target_policies import VERIFICATION_EXECUTABLE_TARGETS
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


def _build_parser(command):
    parser = CustomArgumentParser(prog="cobra")
    subparsers = parser.add_subparsers(dest="command")
    command.register_subparser(subparsers)
    return parser


@pytest.mark.parametrize("target", OFFICIAL_TARGETS)
def test_compile_parser_acepta_targets_canonicos_en_tipo_backend_y_tipos(target):
    parser = _build_parser(CompileCommand())
    args = parser.parse_args(
        [
            "compilar",
            "archivo.co",
            "--tipo",
            target,
            "--backend",
            target,
            "--tipos",
            f"python,{target}",
        ]
    )

    assert args.tipo == target
    assert args.backend == target
    assert args.tipos == ["python", target]


@pytest.mark.parametrize("raw", ("c++", "ensamblador", "C++", "Ensamblador"))
def test_compile_parser_rechaza_aliases_legacy(raw):
    parser = _build_parser(CompileCommand())
    with pytest.raises(SystemExit):
        parser.parse_args(["compilar", "archivo.co", "--tipo", raw])


@pytest.mark.parametrize(
    ("flag", "value"),
    (
        ("--tipo", "fantasy"),
        ("--backend", "fantasy"),
        ("--tipos", "python,fantasy"),
    ),
)
def test_compile_parser_rechaza_lenguajes_no_oficiales(flag, value):
    parser = _build_parser(CompileCommand())
    with pytest.raises(SystemExit):
        parser.parse_args(["compilar", "archivo.co", flag, value])


@pytest.mark.parametrize("target", OFFICIAL_TARGETS)
def test_benchmarks_run_acepta_backends_canonicos(target, monkeypatch):
    mensajes: list[str] = []
    monkeypatch.setattr("pcobra.cobra.cli.commands.benchmarks_cmd.Path.exists", lambda _self: False)
    monkeypatch.setattr("pcobra.cobra.cli.commands.benchmarks_cmd.mostrar_info", lambda m: mensajes.append(m))
    rc = BenchmarksCommand().run(SimpleNamespace(backend=target, iteraciones=1, output=None))
    assert rc == 0


@pytest.mark.parametrize("raw_backend", ("c++", "ensamblador"))
def test_benchmarks_run_rechaza_aliases_legacy(raw_backend, monkeypatch):
    errores: list[str] = []
    monkeypatch.setattr("pcobra.cobra.cli.commands.benchmarks_cmd.Path.exists", lambda _self: False)
    monkeypatch.setattr("pcobra.cobra.cli.commands.benchmarks_cmd.mostrar_error", lambda m: errores.append(m))

    rc = BenchmarksCommand().run(SimpleNamespace(backend=raw_backend, iteraciones=1, output=None))

    assert rc == 1
    assert errores


def test_benchmarks_run_rechaza_backend_no_oficial(monkeypatch):
    errores: list[str] = []
    monkeypatch.setattr("pcobra.cobra.cli.commands.benchmarks_cmd.Path.exists", lambda _self: False)
    monkeypatch.setattr("pcobra.cobra.cli.commands.benchmarks_cmd.mostrar_error", lambda m: errores.append(m))

    rc = BenchmarksCommand().run(SimpleNamespace(backend="fantasy", iteraciones=1, output=None))

    assert rc == 1
    assert errores


@pytest.mark.parametrize("target", VERIFICATION_EXECUTABLE_TARGETS)
def test_verify_parser_acepta_targets_canonicos_en_lenguajes(target):
    parser = _build_parser(VerifyCommand())
    args = parser.parse_args(["verificar", "archivo.co", "--lenguajes", target])
    assert args.lenguajes == [target]


@pytest.mark.parametrize("raw", ("python,c++", "python,ensamblador"))
def test_verify_parser_rechaza_aliases_legacy_y_aplica_restriccion_runtime(raw):
    parser = _build_parser(VerifyCommand())
    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "archivo.co", "--lenguajes", raw])


@pytest.mark.parametrize("raw", ("fantasy", "python,fantasy"))
def test_verify_parser_rechaza_lenguajes_no_oficiales(raw):
    parser = _build_parser(VerifyCommand())
    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "archivo.co", "--lenguajes", raw])


def test_benchmarks_backends_alineado_al_set_canonico():
    assert BACKENDS == OFFICIAL_TARGETS


def test_compile_parser_permite_internal_only_si_flag_temporal_esta_activa(monkeypatch):
    monkeypatch.setenv("COBRA_INTERNAL_LEGACY_TARGETS", "1")
    parser = _build_parser(CompileCommand())
    args = parser.parse_args(["compilar", "archivo.co", "--tipo", "go"])
    assert args.tipo == "go"
