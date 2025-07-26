import argparse
import logging
import sys
from os import environ
from typing import List, Dict, Optional

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
from cobra.cli.commands.jupyter_cmd import JupyterCommand
from cobra.cli.commands.modules_cmd import ModulesCommand
from cobra.cli.commands.package_cmd import PaqueteCommand
from cobra.cli.commands.plugins_cmd import PluginsCommand
from cobra.cli.commands.profile_cmd import ProfileCommand
from cobra.cli.commands.qualia_cmd import QualiaCommand
from cobra.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand
from cobra.cli.commands.verify_cmd import VerifyCommand
from src.cobra.cli.commands.base import BaseCommand
from src.cobra.cli.i18n import _, format_traceback, setup_gettext
from src.cobra.cli.plugin import descubrir_plugins
from src.cobra.cli.utils import messages
from src.cobra.cli.commands import *


class CliConstants:
    DEFAULT_LANGUAGE = "es"
    DEFAULT_COMMAND = "interactive"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    PROGRAM_NAME = "cobra"


class CliApplication:
    def __init__(self) -> None:
        self.parser: Optional[argparse.ArgumentParser] = None
        self.command_map: Dict[str, BaseCommand] = {}

    def initialize(self) -> None:
        setup_gettext()
        self.configure_logging()
        self.parser = self.create_parser()

    def configure_logging(self) -> None:
        logging.basicConfig(
            level=logging.DEBUG,
            format=CliConstants.LOG_FORMAT
        )

    def _add_base_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--format",
            action="store_true",
            help=_("Format file before processing")
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help=_("Show debug messages")
        )
        parser.add_argument(
            "--safe",
            action="store_true",
            help=_("Run in safe mode")
        )
        parser.add_argument(
            "--lang",
            default=environ.get("COBRA_LANG", CliConstants.DEFAULT_LANGUAGE),
            help=_("Interface language code")
        )
        parser.add_argument(
            "--no-color",
            action="store_true",
            help=_("Disable colored output")
        )
        parser.add_argument(
            "--extra-validators",
            help=_("Path to custom validators module")
        )

    def create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=CliConstants.PROGRAM_NAME,
            description=_("CLI for Cobra")
        )
        self._add_base_arguments(parser)
        return parser

    def register_commands(self, subparsers) -> Dict[str, BaseCommand]:
        base_commands = [
            CompileCommand(), ExecuteCommand(), ModulesCommand(),
            DependenciasCommand(), DocsCommand(), EmpaquetarCommand(),
            PaqueteCommand(), CrearCommand(), InitCommand(),
            JupyterCommand(), FletCommand(), ContainerCommand(),
            BenchCommand(), BenchmarksCommand(), BenchmarksV2Command(),
            BenchTranspilersCommand(), BenchThreadsCommand(),
            ProfileCommand(), QualiaCommand(), CacheCommand(),
            TranspilarInversoCommand(), VerifyCommand(),
            PluginsCommand(), InteractiveCommand()
        ]

        all_commands = base_commands + descubrir_plugins()
        command_map = {
            cmd.name: cmd for cmd in all_commands
        }

        for command in all_commands:
            command.register_subparser(subparsers)

        return command_map

    def handle_error(self, exc: Exception, language: str) -> int:
        logging.exception("Unhandled error")
        messages.mostrar_error("An unexpected error occurred")
        print(format_traceback(exc, language))
        return 1

    def _process_arguments(self, argv: List[str]) -> argparse.Namespace:
        if not self.parser:
            raise RuntimeError("Parser not initialized")
        subparsers = self.parser.add_subparsers(dest="command")
        self.command_map = self.register_commands(subparsers)
        self.parser.set_defaults(cmd=self.command_map[CliConstants.DEFAULT_COMMAND])
        return self.parser.parse_args(argv)

    def execute_command(self, args: argparse.Namespace) -> int:
        command = getattr(args, "cmd", self.command_map[CliConstants.DEFAULT_COMMAND])
        try:
            result = command.run(args)
            return 0 if result is None else result
        except Exception as exc:
            return self.handle_error(exc, args.lang)

    def run(self, argv: Optional[List[str]] = None) -> int:
        self.initialize()
        if argv is None:
            argv = [] if "PYTEST_CURRENT_TEST" in environ else sys.argv[1:]

        args = self._process_arguments(argv)
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
