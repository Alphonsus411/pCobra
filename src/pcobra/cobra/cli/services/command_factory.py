"""Factory/registry para resolución de comandos CLI por nombre/capacidad."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Callable

from pcobra.cobra.cli.commands.base import BaseCommand, CommandCapability


@dataclass(frozen=True)
class CommandSpec:
    """Metadatos mínimos para instanciar un comando de forma lazy."""

    name: str
    capability: CommandCapability
    module_path: str
    class_name: str


class CommandFactory:
    """Resuelve instancias de comandos sin imports directos en consumidores."""

    _SPECS: tuple[CommandSpec, ...] = (
        CommandSpec(
            name="ejecutar",
            capability="execute",
            module_path="pcobra.cobra.cli.commands.execute_cmd",
            class_name="ExecuteCommand",
        ),
        CommandSpec(
            name="compilar",
            capability="codegen",
            module_path="pcobra.cobra.cli.commands.compile_cmd",
            class_name="CompileCommand",
        ),
        CommandSpec(
            name="verificar",
            capability="codegen",
            module_path="pcobra.cobra.cli.commands.verify_cmd",
            class_name="VerifyCommand",
        ),
        CommandSpec(
            name="modulos",
            capability="mixed",
            module_path="pcobra.cobra.cli.commands.modules_cmd",
            class_name="ModulesCommand",
        ),
    )

    def __init__(self) -> None:
        self._spec_by_name: dict[str, CommandSpec] = {spec.name: spec for spec in self._SPECS}

    def create(self, command_name: str) -> BaseCommand:
        """Crea una instancia de comando por nombre lógico."""
        spec = self._spec_by_name.get(command_name)
        if spec is None:
            raise ValueError(f"Comando no registrado en factory: {command_name}")
        return self._create_from_spec(spec)

    def create_by_capability(self, capability: CommandCapability) -> list[BaseCommand]:
        """Crea todas las instancias asociadas a una capacidad."""
        return [
            self._create_from_spec(spec)
            for spec in self._SPECS
            if spec.capability == capability
        ]

    @staticmethod
    def _create_from_spec(spec: CommandSpec) -> BaseCommand:
        module = import_module(spec.module_path)
        command_class: Callable[[], BaseCommand] = getattr(module, spec.class_name)
        return command_class()
