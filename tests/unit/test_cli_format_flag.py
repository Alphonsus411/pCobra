from argparse import Namespace
from contextlib import ExitStack
from unittest.mock import patch

from cobra.cli.commands.execute_cmd import ExecuteCommand
from cobra.cli.commands.profile_cmd import ProfileCommand


def test_execute_command_with_format_invokes_formatter(tmp_path):
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
            patch("cobra.cli.commands.execute_cmd.module_map.get_toml_map", return_value={})
        )
        stack.enter_context(
            patch("cobra.cli.commands.execute_cmd.sandbox_module.validar_dependencias")
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_limitar_recursos", lambda self, funcion: funcion())
        )
        stack.enter_context(
            patch.object(ExecuteCommand, "_ejecutar_normal", lambda self, codigo, seguro, extra: 0)
        )
        mock_formatear = stack.enter_context(
            patch("cobra.cli.commands.execute_cmd.ExecuteCommand._formatear_codigo", return_value=True)
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
