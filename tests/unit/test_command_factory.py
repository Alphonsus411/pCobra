import types
import sys

import pytest

from cobra.cli.services.command_factory import CommandFactory
from pcobra.cobra.cli.services.command_factory import load_command_class
from pcobra.cobra.cli.commands.base import BaseCommand


def test_command_factory_resuelve_por_nombre():
    factory = CommandFactory()

    ejecutar = factory.create("ejecutar")
    compilar = factory.create("compilar")
    verificar = factory.create("verificar")
    modulos = factory.create("modulos")

    assert ejecutar.name == "ejecutar"
    assert compilar.name == "compilar"
    assert verificar.name == "verificar"
    assert modulos.name == "modulos"


def test_command_factory_resuelve_por_capacidad():
    factory = CommandFactory()

    execute_commands = factory.create_by_capability("execute")
    codegen_commands = factory.create_by_capability("codegen")

    assert [cmd.name for cmd in execute_commands] == ["ejecutar"]
    assert {cmd.name for cmd in codegen_commands} == {"compilar", "verificar"}


def test_load_command_class_valida_contrato_basecommand():
    module_name = "tests.fake_invalid_cli_command"
    fake_module = types.ModuleType(module_name)

    class ComandoInvalido:
        pass

    setattr(fake_module, "ComandoInvalido", ComandoInvalido)
    sys.modules[module_name] = fake_module
    try:
        with pytest.raises(TypeError, match="debe heredar de BaseCommand"):
            load_command_class(module_name, "ComandoInvalido")
    finally:
        sys.modules.pop(module_name, None)


def test_load_command_class_acepta_subclase_valida():
    module_name = "tests.fake_valid_cli_command"
    fake_module = types.ModuleType(module_name)

    class ComandoValido(BaseCommand):
        name = "fake"

        def register_subparser(self, subparsers):
            return subparsers

        def run(self, args):
            return 0

    setattr(fake_module, "ComandoValido", ComandoValido)
    sys.modules[module_name] = fake_module
    try:
        loaded = load_command_class(module_name, "ComandoValido")
        assert loaded is ComandoValido
    finally:
        sys.modules.pop(module_name, None)
