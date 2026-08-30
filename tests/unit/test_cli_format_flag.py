from argparse import Namespace
from contextlib import ExitStack
import sys
from unittest.mock import Mock, patch

from cobra.cli.commands.execute_cmd import ExecuteCommand
from cobra.cli.commands.profile_cmd import ProfileCommand


def test_execute_command_with_format_propagates_flag_to_run_service(tmp_path):
    archivo = tmp_path / "programa.cobra"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")

    args = Namespace(
        archivo=str(archivo),
        sandbox=False,
        contenedor=None,
        depurar=False,
        debug=False,
        verbose=0,
        seguro=True,
        extra_validators=None,
        formatear=True,
    )

    comando = ExecuteCommand()

    with patch.object(comando._service, "run", return_value=0) as mock_run:
        resultado = comando.run(args)

    assert resultado == 0

    request = mock_run.call_args.args[0]
    assert request.archivo == str(archivo)
    assert request.formatear is True


def test_profile_command_with_format_invokes_formatter(tmp_path):
    archivo = tmp_path / "perfilado.cobra"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")

    args = Namespace(
        archivo=str(archivo),
        output=str(tmp_path / "salida.prof"),
        ui=None,
        depurar=False,
        seguro=False,
        extra_validators=None,
        analysis=False,
        formatear=True,
    )

    comando = ProfileCommand()

    class DummyProfiler:
        def enable(self):
            return None

        def disable(self):
            return None

        def dump_stats(self, _ruta):
            return None

    lexer_mock = Mock()
    parser_mock = Mock()
    interpreter_factory = Mock()
    mock_formatear = Mock(return_value=True)

    lexer_mock.return_value.tokenizar.return_value = []
    parser_mock.return_value.parsear.return_value = []
    interpreter_factory.return_value.ejecutar_ast.return_value = None

    fake_cprofile = Mock()
    fake_cprofile.Profile.return_value = DummyProfiler()

    globals_patch = {
        "normalizar_validadores_extra": Mock(return_value=None),
        "validar_archivo_existente": Mock(),
        "cli_toml_map": Mock(return_value={}),
        "validar_dependencias": Mock(),
        "format_code_with_black": mock_formatear,
        "Lexer": lexer_mock,
        "Parser": parser_mock,
        "construir_interprete_seguro_canonico": interpreter_factory,
        "cProfile": fake_cprofile,
        "mostrar_info": Mock(),
    }

    with patch.dict(ProfileCommand.run.__globals__, globals_patch, clear=False):
        resultado = comando.run(args)

    assert resultado == 0
    mock_formatear.assert_called_once_with(str(archivo))


def _build_execute_args(archivo, **overrides):
    args = {
        "archivo": str(archivo),
        "sandbox": False,
        "contenedor": None,
        "depurar": False,
        "debug": False,
        "verbose": 0,
        "seguro": True,
        "extra_validators": None,
        "formatear": False,
    }
    args.update(overrides)
    return Namespace(**args)


def test_execute_command_debug_flag_is_forwarded_to_run_service(tmp_path):
    archivo = tmp_path / "programa_debug.cobra"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")

    args = _build_execute_args(archivo, debug=True)
    comando = ExecuteCommand()

    with patch.object(comando._service, "run", return_value=0) as mock_run:
        resultado = comando.run(args)

    assert resultado == 0

    request = mock_run.call_args.args[0]
    assert request.debug is True


def test_execute_command_verbose_flag_is_forwarded_to_run_service(tmp_path):
    archivo = tmp_path / "programa_verbose.cobra"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")

    args = _build_execute_args(archivo, verbose=1)
    comando = ExecuteCommand()

    with patch.object(comando._service, "run", return_value=0) as mock_run:
        resultado = comando.run(args)

    assert resultado == 0

    request = mock_run.call_args.args[0]
    assert request.verbose == 1


def test_execute_command_depurar_legacy_is_forwarded_to_run_service(tmp_path):
    archivo = tmp_path / "programa_legacy.cobra"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")

    args = _build_execute_args(archivo, depurar=True)
    comando = ExecuteCommand()

    with patch.object(comando._service, "run", return_value=0) as mock_run:
        resultado = comando.run(args)

    assert resultado == 0

    request = mock_run.call_args.args[0]
    assert request.depurar is True


def test_execute_command_forwards_project_file_to_run_service(tmp_path):
    proyecto = tmp_path / "demo"
    proyecto.mkdir()

    (proyecto / "cobra.toml").write_text("", encoding="utf-8")

    archivo = proyecto / "programa.cobra"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")

    args = _build_execute_args(archivo)
    comando = ExecuteCommand()

    with patch.object(comando._service, "run", return_value=0) as mock_run:
        resultado = comando.run(args)

    assert resultado == 0

    request = mock_run.call_args.args[0]
    assert request.archivo == str(archivo)
