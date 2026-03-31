from argparse import Namespace
from contextlib import ExitStack
import logging
import sys
from unittest.mock import Mock, patch

from cobra.cli.commands.execute_cmd import ExecuteCommand
from cobra.cli.commands.profile_cmd import ProfileCommand


def test_execute_command_with_format_invokes_formatter(tmp_path):
    import cobra.cli.commands.execute_cmd as execute_module

    archivo = tmp_path / "programa.co"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")

    args = Namespace(
        archivo=str(archivo),
        sandbox=False,
        contenedor=None,
        depurar=False,
        seguro=True,
        extra_validators=None,
        formatear=True,
    )

    comando = ExecuteCommand()

    with ExitStack() as stack:
        stack.enter_context(
            patch.object(execute_module.module_map, "get_toml_map", return_value={})
        )
        stack.enter_context(
            patch.object(execute_module, "validar_dependencias")
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_limitar_recursos", lambda self, funcion: funcion())
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_ejecutar_normal", lambda self, codigo, seguro, extra: 0)
        )
        mock_formatear = stack.enter_context(
            patch.object(comando, "_formatear_codigo", return_value=True)
        )

        resultado = comando.run(args)

    assert resultado == 0
    mock_formatear.assert_called_once_with(str(archivo))


def test_profile_command_with_format_invokes_formatter(tmp_path):
    archivo = tmp_path / "perfilado.co"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")

    args = Namespace(
        archivo=str(archivo),
        output=str(tmp_path / "salida.prof"),
        ui=None,
        depurar=False,
        seguro=True,
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

    with ExitStack() as stack:
        stack.enter_context(
            patch("cobra.cli.commands.profile_cmd.normalizar_validadores_extra", return_value=None)
        )
        stack.enter_context(patch("cobra.cli.commands.profile_cmd.validar_archivo_existente"))
        stack.enter_context(patch("cobra.cli.commands.profile_cmd.validar_dependencias"))
        lexer_mock = stack.enter_context(patch("cobra.cli.commands.profile_cmd.Lexer"))
        parser_mock = stack.enter_context(patch("cobra.cli.commands.profile_cmd.Parser"))
        interp_mock = stack.enter_context(patch("cobra.cli.commands.profile_cmd.InterpretadorCobra"))
        stack.enter_context(
            patch("cobra.cli.commands.profile_cmd.construir_cadena", return_value=lambda nodo: None)
        )
        stack.enter_context(
            patch("cobra.cli.commands.profile_cmd.cProfile.Profile", return_value=DummyProfiler())
        )
        stack.enter_context(patch("cobra.cli.commands.profile_cmd.mostrar_info"))
        mock_formatear = stack.enter_context(
            patch("cobra.cli.commands.execute_cmd.ExecuteCommand._formatear_codigo", return_value=True)
        )

        lexer_mock.return_value.tokenizar.return_value = []
        parser_mock.return_value.parsear.return_value = []
        interp_mock._cargar_validadores.return_value = []
        interp_mock.return_value.ejecutar_ast.return_value = None

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


def test_execute_command_debug_flag_sets_debug_logger(tmp_path):
    archivo = tmp_path / "programa_debug.co"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")
    args = _build_execute_args(archivo, debug=True)
    comando = ExecuteCommand()

    with ExitStack() as stack:
        stack.enter_context(
            patch("cobra.cli.commands.execute_cmd.module_map.get_toml_map", return_value={})
        )
        stack.enter_context(
            patch("cobra.cli.commands.execute_cmd.validar_dependencias")
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_limitar_recursos", lambda self, funcion: funcion())
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_ejecutar_normal", lambda self, codigo, seguro, extra: 0)
        )
        resultado = comando.run(args)

    assert resultado == 0
    assert comando.logger.level == logging.DEBUG


def test_execute_command_verbose_flag_sets_debug_logger(tmp_path):
    archivo = tmp_path / "programa_verbose.co"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")
    args = _build_execute_args(archivo, verbose=1)
    comando = ExecuteCommand()

    with ExitStack() as stack:
        stack.enter_context(
            patch("cobra.cli.commands.execute_cmd.module_map.get_toml_map", return_value={})
        )
        stack.enter_context(
            patch("cobra.cli.commands.execute_cmd.validar_dependencias")
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_limitar_recursos", lambda self, funcion: funcion())
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_ejecutar_normal", lambda self, codigo, seguro, extra: 0)
        )
        resultado = comando.run(args)

    assert resultado == 0
    assert comando.logger.level == logging.DEBUG


def test_execute_command_depurar_legacy_still_supported(tmp_path):
    archivo = tmp_path / "programa_legacy.co"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")
    args = _build_execute_args(archivo, depurar=True)
    comando = ExecuteCommand()

    with ExitStack() as stack:
        stack.enter_context(
            patch("cobra.cli.commands.execute_cmd.module_map.get_toml_map", return_value={})
        )
        stack.enter_context(
            patch("cobra.cli.commands.execute_cmd.validar_dependencias")
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_limitar_recursos", lambda self, funcion: funcion())
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_ejecutar_normal", lambda self, codigo, seguro, extra: 0)
        )
        resultado = comando.run(args)

    assert resultado == 0
    assert comando.logger.level == logging.DEBUG


def test_execute_command_pasa_raiz_proyecto_a_validar_dependencias(tmp_path, monkeypatch):
    proyecto = tmp_path / "demo"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("", encoding="utf-8")
    archivo = proyecto / "programa.co"
    archivo.write_text("imprimir('hola')\n", encoding="utf-8")
    args = _build_execute_args(archivo)
    comando = ExecuteCommand()
    execute_module = sys.modules[comando.__class__.__module__]
    mock_validar = Mock()
    monkeypatch.setitem(ExecuteCommand.run.__globals__, "validar_dependencias", mock_validar)

    with ExitStack() as stack:
        stack.enter_context(
            patch.object(execute_module.module_map, "get_toml_map", return_value={})
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_limitar_recursos", lambda self, funcion: funcion())
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_ejecutar_normal", lambda self, codigo, seguro, extra: 0)
        )
        resultado = comando.run(args)

    assert resultado == 0
    assert mock_validar.call_args.kwargs["base_dir"] == str(proyecto)
