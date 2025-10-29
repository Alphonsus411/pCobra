import argparse
import logging
import sys
from enum import Enum
from os import environ
from pathlib import Path
from typing import List, Dict, Optional, Type, Any, ContextManager
from contextlib import contextmanager

from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.bench_cmd import BenchCommand
from pcobra.cobra.cli.commands.bench_transpilers_cmd import BenchTranspilersCommand
from pcobra.cobra.cli.commands.benchmarks_cmd import BenchmarksCommand
from pcobra.cobra.cli.commands.benchmarks2_cmd import BenchmarksV2Command
from pcobra.cobra.cli.commands.benchthreads_cmd import BenchThreadsCommand
from pcobra.cobra.cli.commands.cache_cmd import CacheCommand
from pcobra.cobra.cli.commands.compile_cmd import CompileCommand, LANG_CHOICES
from pcobra.cobra.cli.commands.container_cmd import ContainerCommand
from pcobra.cobra.cli.commands.crear_cmd import CrearCommand
from pcobra.cobra.cli.commands.dependencias_cmd import DependenciasCommand
from pcobra.cobra.cli.commands.docs_cmd import DocsCommand
from pcobra.cobra.cli.commands.empaquetar_cmd import EmpaquetarCommand
from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand
from pcobra.cobra.cli.commands.flet_cmd import FletCommand
from pcobra.cobra.cli.commands.init_cmd import InitCommand
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.commands.agix_cmd import AgixCommand
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.cobra.cli.commands.jupyter_cmd import JupyterCommand
from pcobra.cobra.cli.commands.modules_cmd import ModulesCommand
from pcobra.cobra.cli.commands.package_cmd import PaqueteCommand
from pcobra.cobra.cli.commands.plugins_cmd import PluginsCommand
from pcobra.cobra.cli.commands.profile_cmd import ProfileCommand
from pcobra.cobra.cli.commands.qualia_cmd import QualiaCommand
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand, ORIGIN_CHOICES
from pcobra.cobra.cli.commands.verify_cmd import VerifyCommand
from pcobra.cobra.cli.i18n import _, format_traceback, setup_gettext
from pcobra.cobra.cli.plugin import descubrir_plugins
from pcobra.cobra.cli.utils import messages
from pcobra.cobra.cli.utils import config as config_module
from pcobra.cobra.cli.utils.autocomplete import (
    autocomplete_available,
    directories_completer,
    enable_autocomplete,
    files_completer,
)

# Metadata injected at build time
CLI_VERSION = environ.get("COBRA_CLI_VERSION", "dev")
CLI_COMMIT = environ.get("COBRA_CLI_COMMIT", "unknown")


class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR


class AppConfig:
    # Cargar configuración desde archivo
    try:
        config_data = config_module.load_config()
    except Exception as e:  # pragma: no cover - handled by tests
        logging.error(f"Failed to load configuration: {e}")
        config_data: Dict[str, str] = {}
    DEFAULT_LANGUAGE = config_data.get("language", "es")
    DEFAULT_COMMAND = config_data.get("default_command", "interactive")
    LOG_FORMAT = config_data.get("log_format", "%(asctime)s - %(levelname)s - %(message)s")
    PROGRAM_NAME = config_data.get("program_name", "cobra")
    BASE_COMMAND_CLASSES: List[Type[BaseCommand]] = [
        InteractiveCommand, CompileCommand, ExecuteCommand, ModulesCommand,
        DependenciasCommand, DocsCommand, EmpaquetarCommand,
        PaqueteCommand, CrearCommand, InitCommand,
        JupyterCommand, FletCommand, ContainerCommand,
        BenchCommand, BenchmarksCommand, BenchmarksV2Command,
        BenchTranspilersCommand, BenchThreadsCommand,
        ProfileCommand, QualiaCommand, CacheCommand,
        TranspilarInversoCommand, VerifyCommand,
        PluginsCommand, AgixCommand
    ]


class CommandRegistry:
    def __init__(self, interpreter: Optional[InterpretadorCobra] = None) -> None:
        self.commands: Dict[str, BaseCommand] = {}
        self.interpreter = interpreter

    def create_command(self, command_class: Type[BaseCommand]) -> BaseCommand:
        try:
            if command_class.__name__ == "InteractiveCommand":
                if not self.interpreter:
                    raise ValueError("Interpreter required for InteractiveCommand")
                return command_class(self.interpreter)
            return command_class()
        except Exception as e:
            logging.error(f"Error creating command {command_class.__name__}: {e}")
            raise

    def register_base_commands(self, subparsers: Any) -> Dict[str, BaseCommand]:
        base_commands = []
        for cmd_class in AppConfig.BASE_COMMAND_CLASSES:
            try:
                base_commands.append(self.create_command(cmd_class))
            except Exception as e:
                logging.error(f"Failed to create command {cmd_class.__name__}: {e}")
                continue

        plugin_commands = descubrir_plugins()
        all_commands = base_commands + plugin_commands
        self.commands = {cmd.name: cmd for cmd in all_commands}

        for command in all_commands:
            try:
                command.register_subparser(subparsers)
            except Exception as e:
                logging.error(f"Failed to register subparser for {command.name}: {e}")
                del self.commands[command.name]

        if AppConfig.DEFAULT_COMMAND not in self.commands:
            fallback = "interactive" if "interactive" in self.commands else next(iter(self.commands), None)
            logging.warning(
                "Default command '%s' not found. Falling back to '%s'", AppConfig.DEFAULT_COMMAND, fallback
            )
            AppConfig.DEFAULT_COMMAND = fallback

        return self.commands

    def get_default_command(self) -> Optional[BaseCommand]:
        return self.commands.get(AppConfig.DEFAULT_COMMAND)


class CliApplication:
    def __init__(self) -> None:
        self.parser: Optional[CustomArgumentParser] = None
        self.interpreter: Optional[InterpretadorCobra] = None
        self.command_registry: Optional[CommandRegistry] = None

    @contextmanager
    def resource_management(self) -> ContextManager[None]:
        try:
            yield
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        if self.interpreter and hasattr(self.interpreter, "cleanup"):
            self.interpreter.cleanup()
        logging.shutdown()

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

    def _configure_cli_options(self, parser: CustomArgumentParser) -> None:
        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {CLI_VERSION} (commit {CLI_COMMIT})",
            help=_("Show version information and exit"),
        )
        parser.add_argument("--ayuda", action="help",
                          help=_("Muestra esta ayuda y termina"))
        parser.add_argument("--format", action="store_true",
                          help=_("Format file before processing"))
        parser.add_argument("--debug", action="store_true",
                          help=_("Show debug messages"))
        parser.add_argument("-v", "--verbose", action="count", default=0,
                          help=_("Incrementa el nivel de detalle"))
        parser.add_argument(
            "--no-safe",
            "--no-seguro",
            dest="seguro",
            action="store_false",
            help=_("Run without safe mode"),
        )
        parser.set_defaults(seguro=True)
        parser.add_argument("--lang",
                          default=environ.get("COBRA_LANG", AppConfig.DEFAULT_LANGUAGE),
                          help=_("Interface language code"))
        parser.add_argument("--no-color", action="store_true",
                          help=_("Disable colored output"))
        parser.add_argument("--extra-validators",
                          help=_("Path to custom validators module"),
                          type=Path)

    def _configure_autocomplete(self, parser: CustomArgumentParser) -> None:
        """Configura autocompletado para argumentos comunes.

        Recorre recursivamente todos los subparsers y asigna un completer
        apropiado para argumentos que representan rutas de archivos o
        directorios.
        """
        file_args = {
            "archivo",
            "ruta",
            "path",
            "fuente",
            "pkg",
            "notebook",
            "extra_validators",
        }
        dir_args = {"directorio", "carpeta"}

        for action in parser._actions:
            choices = getattr(action, "choices", None)
            if isinstance(choices, dict) or isinstance(action, argparse._SubParsersAction):
                if isinstance(choices, dict):
                    for sub in choices.values():
                        self._configure_autocomplete(sub)
                continue
            if action.dest in file_args:
                action.completer = files_completer()
            elif action.dest in dir_args:
                action.completer = directories_completer()

    def _build_argument_parser(self) -> CustomArgumentParser:
        parser = CustomArgumentParser(
            prog=AppConfig.PROGRAM_NAME,
            description=_("CLI for Cobra")
        )
        self._configure_cli_options(parser)
        return parser

    def _parse_arguments(self, argv: List[str]) -> argparse.Namespace:
        if not self.parser or not self.command_registry:
            raise RuntimeError("Application not properly initialized")
            
        subparsers = self.parser.add_subparsers(dest="command", parser_class=CustomArgumentParser)
        self.command_registry.register_base_commands(subparsers)

        menu_parser = subparsers.add_parser("menu", help=_("Modo interactivo"))
        menu_parser.set_defaults(cmd="menu")

        default_command = self.command_registry.get_default_command()
        if default_command:
            self.parser.set_defaults(cmd=default_command)
        if autocomplete_available():
            self._configure_autocomplete(self.parser)
            enable_autocomplete(self.parser)
        else:
            logging.getLogger(__name__).debug(
                "Autocompletado deshabilitado: argcomplete no está instalado.",
            )

        return self.parser.parse_args(argv)

    def _handle_execution_error(self, exc: Exception, language: str) -> int:
        if isinstance(exc, ValueError):
            messages.mostrar_error(_("Value error: {}").format(str(exc)))
        elif isinstance(exc, FileNotFoundError):
            messages.mostrar_error(str(exc))
        else:
            messages.mostrar_error(_("An unexpected error occurred"))

        logging.exception("Error in execution")
        print(format_traceback(exc, language))
        return 1

    def run_menu(self) -> int:
        if not self.command_registry:
            raise RuntimeError("Command registry not initialized")

        print(_("Lenguajes destino disponibles:"))
        print(", ".join(LANG_CHOICES))
        print(_("Lenguajes de origen disponibles:"))
        print(", ".join(ORIGIN_CHOICES))

        if not input(_("¿Desea transpilar? (s/n): ")).strip().lower().startswith("s"):
            return 0

        if input(_("¿Transpilar desde Cobra a otro lenguaje? (s/n): ")).strip().lower().startswith("s"):
            archivo = input(_("Ruta al archivo Cobra: ")).strip()
            destino = input(_("Lenguaje destino: ")).strip().lower()
            args = argparse.Namespace(archivo=archivo, tipo=destino, backend=None, tipos=None)
            compile_cmd = self.command_registry.commands.get("compilar")
            if not compile_cmd:
                messages.mostrar_error(_("Comando 'compilar' no disponible"))
                return 1
            return compile_cmd.run(args)
        else:
            archivo = input(_("Ruta al archivo origen: ")).strip()
            origen = input(_("Lenguaje origen: ")).strip().lower()
            destino = input(_("Lenguaje destino: ")).strip().lower()
            inv_cmd = self.command_registry.commands.get("transpilar-inverso")
            if not inv_cmd:
                messages.mostrar_error(_("Comando 'transpilar-inverso' no disponible"))
                return 1
            args = argparse.Namespace(archivo=archivo, origen=origen, destino=destino)
            return inv_cmd.run(args)

    def execute_command(self, args: argparse.Namespace) -> int:
        if not self.command_registry:
            raise RuntimeError("Command registry not initialized")
            
        command = getattr(args, "cmd", self.command_registry.get_default_command())
        if command == "menu":
            return self.run_menu()
        if not command:
            self.parser.print_help()
            messages.mostrar_error(_("Comando inválido. Use --help para ver opciones."))
            return 1
            
        try:
            result = command.run(args)
            return 0 if result is None else result
        except Exception as exc:
            return self._handle_execution_error(exc, args.lang)

    def run(self, argv: Optional[List[str]] = None) -> int:
        with self.resource_management():
            self.initialize()
            if argv is None:
                argv = [] if "PYTEST_CURRENT_TEST" in environ else sys.argv[1:]

            try:
                args = self._parse_arguments(argv)
                log_level = logging.DEBUG if args.verbose > 0 or args.debug else logging.INFO
                logging.getLogger().setLevel(log_level)
                setup_gettext(args.lang)
                messages.disable_colors(args.no_color)
                messages.mostrar_logo()

                return self.execute_command(args)
            except Exception as e:
                logging.exception("Fatal error in application")
                messages.mostrar_error(_("Fatal error: {}").format(str(e)))
                return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    application = CliApplication()
    return application.run(argv)


if __name__ == "__main__":
    sys.exit(main())
