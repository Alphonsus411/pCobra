import argparse
import logging
import sys
from enum import Enum
from os import environ
from pathlib import Path
from typing import List, Dict, Optional, Type

from cobra.cli.commands.base import BaseCommand
from cobra.cli.commands.bench_cmd import BenchCommand
from cobra.cli.commands.bench_transpilers_cmd import BenchTranspilersCommand
from cobra.cli.commands.benchmarks2_cmd import BenchmarksV2Command
from cobra.cli.commands.benchmarks_cmd import BenchmarksCommand
from cobra.cli.commands.benchthreads_cmd import BenchThreadsCommand
from cobra.cli.commands.cache_cmd import CacheCommand
from cobra.cli.commands.compile_cmd import CompileCommand
from cobra.cli.commands.container_cmd import ContainerCommand
from cobra.cli.commands.crear_cmd import CrearCommand
from cobra.cli.commands.dependencias_cmd import DependenciasCommand
from cobra.cli.commands.docs_cmd import DocsCommand
from cobra.cli.commands.empaquetar_cmd import EmpaquetarCommand
from cobra.cli.commands.execute_cmd import ExecuteCommand
from cobra.cli.commands.flet_cmd import FletCommand
from cobra.cli.commands.init_cmd import InitCommand
from cobra.cli.commands.interactive_cmd import InteractiveCommand
from core.interpreter import InterpretadorCobra
from cobra.cli.commands.jupyter_cmd import JupyterCommand
from cobra.cli.commands.modules_cmd import ModulesCommand
from cobra.cli.commands.package_cmd import PaqueteCommand
from cobra.cli.commands.plugins_cmd import PluginsCommand
from cobra.cli.commands.profile_cmd import ProfileCommand
from cobra.cli.commands.qualia_cmd import QualiaCommand
from cobra.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand
from cobra.cli.commands.verify_cmd import VerifyCommand
from cobra.cli.i18n import _, format_traceback, setup_gettext
from cobra.cli.plugin import descubrir_plugins
from cobra.cli.utils import messages


class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR


class AppConfig:
    DEFAULT_LANGUAGE = "es"
    DEFAULT_COMMAND = "interactive"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    PROGRAM_NAME = "cobra"
    BASE_COMMAND_CLASSES: List[Type[BaseCommand]] = [
        # Las clases de comandos importadas anteriormente
        CompileCommand, ExecuteCommand, ModulesCommand,
        DependenciasCommand, DocsCommand, EmpaquetarCommand,
        PaqueteCommand, CrearCommand, InitCommand,
        JupyterCommand, FletCommand, ContainerCommand,
        BenchCommand, BenchmarksCommand, BenchmarksV2Command,
        BenchTranspilersCommand, BenchThreadsCommand,
        ProfileCommand, QualiaCommand, CacheCommand,
        TranspilarInversoCommand, VerifyCommand,
        PluginsCommand, InteractiveCommand
    ]


class CommandRegistry:
    def __init__(self, interpreter: Optional[InterpretadorCobra] = None):
        self.commands: Dict[str, BaseCommand] = {}
        self.interpreter = interpreter

    def create_command(self, command_class: Type[BaseCommand]) -> BaseCommand:
        if command_class is InteractiveCommand:
            return command_class(self.interpreter)
        return command_class()

    def register_base_commands(self, subparsers) -> Dict[str, BaseCommand]:
        base_commands = [self.create_command(cmd_class) for cmd_class in AppConfig.BASE_COMMAND_CLASSES]
        plugin_commands = descubrir_plugins()
        all_commands = base_commands + plugin_commands
        self.commands = {cmd.name: cmd for cmd in all_commands}

        for command in all_commands:
            command.register_subparser(subparsers)
        return self.commands

    def get_default_command(self) -> BaseCommand:
        return self.commands[AppConfig.DEFAULT_COMMAND]


class CliApplication:
    def __init__(self) -> None:
        self.parser: Optional[argparse.ArgumentParser] = None
        self.interpreter: Optional[InterpretadorCobra] = None
        self.command_registry: Optional[CommandRegistry] = None

    def initialize(self) -> None:
        setup_gettext()
        self._setup_logging()
        self.interpreter = InterpretadorCobra()
        self.command_registry = CommandRegistry(self.interpreter)
        self.parser = self._build_argument_parser()

    def _setup_logging(self) -> None:
        logging.basicConfig(
            level=LogLevel.INFO.value,
            format=AppConfig.LOG_FORMAT
        )

    def _configure_cli_options(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--format", action="store_true",
                            help=_("Format file before processing"))
        parser.add_argument("--debug", action="store_true",
                            help=_("Show debug messages"))
        parser.add_argument("--safe", action="store_true",
                            help=_("Run in safe mode"))
        parser.add_argument("--lang",
                            default=environ.get("COBRA_LANG", AppConfig.DEFAULT_LANGUAGE),
                            help=_("Interface language code"))
        parser.add_argument("--no-color", action="store_true",
                            help=_("Disable colored output"))
        parser.add_argument("--extra-validators",
                            help=_("Path to custom validators module"),
                            type=Path)

    def _build_argument_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=AppConfig.PROGRAM_NAME,
            description=_("CLI for Cobra")
        )
        self._configure_cli_options(parser)
        return parser

    def _parse_arguments(self, argv: List[str]) -> argparse.Namespace:
        if not self.parser:
            raise RuntimeError("Parser not initialized")
        subparsers = self.parser.add_subparsers(dest="command")
        self.command_registry.register_base_commands(subparsers)
        self.parser.set_defaults(cmd=self.command_registry.get_default_command())
        return self.parser.parse_args(argv)

    def _handle_execution_error(self, exc: Exception, language: str) -> int:
        logging.exception("Unhandled error")
        messages.mostrar_error("An unexpected error occurred")
        print(format_traceback(exc, language))
        return 1

    def execute_command(self, args: argparse.Namespace) -> int:
        command = getattr(args, "cmd", self.command_registry.get_default_command())
        try:
            result = command.run(args)
            return 0 if result is None else result
        except Exception as exc:
            return self._handle_execution_error(exc, args.lang)

    def run(self, argv: Optional[List[str]] = None) -> int:
        self.initialize()
        if argv is None:
            argv = [] if "PYTEST_CURRENT_TEST" in environ else sys.argv[1:]

        args = self._parse_arguments(argv)
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        setup_gettext(args.lang)
        messages.disable_colors(args.no_color)
        messages.mostrar_logo()

        return self.execute_command(args)


def main(argv=None) -> int:
    """Main entry point for the CLI."""
    application = CliApplication()
    return application.run(argv)


if __name__ == "__main__":
    sys.exit(main())
