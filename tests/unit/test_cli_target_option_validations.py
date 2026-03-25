from types import SimpleNamespace

import pytest

from pcobra.cobra.cli.commands.benchmarks_cmd import BACKENDS, BenchmarksCommand
from pcobra.cobra.cli.commands.compile_cmd import CompileCommand
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
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


@pytest.mark.parametrize(
    ("flag", "value", "expected"),
    (
        ("--tipo", "c++", "cpp"),
        ("--tipo", "ensamblador", "asm"),
        ("--backend", "C++", "cpp"),
        ("--backend", "Ensamblador", "asm"),
    ),
)
def test_compile_parser_normaliza_aliases_permitidos(flag, value, expected):
    parser = _build_parser(CompileCommand())
    args = parser.parse_args(["compilar", "archivo.co", flag, value])

    assert getattr(args, flag.lstrip("-")) == expected


@pytest.mark.parametrize("raw", ("python,c++", "python,Ensamblador"))
def test_compile_parser_normaliza_aliases_en_tipos(raw):
    parser = _build_parser(CompileCommand())
    args = parser.parse_args(["compilar", "archivo.co", "--tipos", raw])

    assert args.tipos[0] == "python"
    assert args.tipos[1] in {"cpp", "asm"}


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
    assert any(target in m for m in mensajes)


@pytest.mark.parametrize(
    ("raw_backend", "canonical"),
    (("c++", "cpp"), ("ensamblador", "asm")),
)
def test_benchmarks_run_normaliza_aliases_permitidos(raw_backend, canonical, monkeypatch):
    mensajes: list[str] = []
    monkeypatch.setattr("pcobra.cobra.cli.commands.benchmarks_cmd.Path.exists", lambda _self: False)
    monkeypatch.setattr("pcobra.cobra.cli.commands.benchmarks_cmd.mostrar_info", lambda m: mensajes.append(m))

    rc = BenchmarksCommand().run(SimpleNamespace(backend=raw_backend, iteraciones=1, output=None))

    assert rc == 0
    assert any(canonical in m for m in mensajes)


def test_benchmarks_run_rechaza_backend_no_oficial(monkeypatch):
    errores: list[str] = []
    monkeypatch.setattr("pcobra.cobra.cli.commands.benchmarks_cmd.Path.exists", lambda _self: False)
    monkeypatch.setattr("pcobra.cobra.cli.commands.benchmarks_cmd.mostrar_error", lambda m: errores.append(m))

    rc = BenchmarksCommand().run(SimpleNamespace(backend="fantasy", iteraciones=1, output=None))

    assert rc == 1
    assert errores


@pytest.mark.parametrize("target", ("python", "rust", "javascript", "cpp"))
def test_verify_parser_acepta_targets_canonicos_en_lenguajes(target):
    parser = _build_parser(VerifyCommand())
    args = parser.parse_args(["verificar", "archivo.co", "--lenguajes", target])
    assert args.lenguajes == [target]


@pytest.mark.parametrize(
    ("raw", "expected"),
    (("python,c++", ["python", "cpp"]), ("python,ensamblador", None)),
)
def test_verify_parser_normaliza_aliases_y_aplica_restriccion_runtime(raw, expected):
    parser = _build_parser(VerifyCommand())
    if expected is None:
        with pytest.raises(SystemExit):
            parser.parse_args(["verificar", "archivo.co", "--lenguajes", raw])
        return
    args = parser.parse_args(["verificar", "archivo.co", "--lenguajes", raw])
    assert args.lenguajes == expected


@pytest.mark.parametrize("raw", ("fantasy", "python,fantasy"))
def test_verify_parser_rechaza_lenguajes_no_oficiales(raw):
    parser = _build_parser(VerifyCommand())
    with pytest.raises(SystemExit):
        parser.parse_args(["verificar", "archivo.co", "--lenguajes", raw])


def test_benchmarks_backends_alineado_al_set_canonico():
    assert BACKENDS == OFFICIAL_TARGETS
