import argparse
import logging
import os
import secrets
import sys
from os import environ
from pathlib import Path
from typing import List, Dict, Optional, Type, Any, ContextManager
from contextlib import contextmanager

from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.target_policies import OFFICIAL_TRANSPILATION_TARGETS
from pcobra.cobra.core.interpreter import InterpretadorCobra
from pcobra.cobra.cli.internal_compat.legacy_targets import (
    LEGACY_BACKENDS_FEATURE_FLAG,
    is_internal_legacy_targets_enabled,
)
from pcobra.cobra.cli.i18n import _, format_traceback, setup_gettext
from pcobra.cobra.cli.mode_policy import (
    CLI_MODOS_PERMITIDOS,
    MODO_POR_DEFECTO,
    validar_politica_modo,
)
from pcobra.cobra.cli.public_command_policy import (
    COMMAND_VISIBILITY_MATRIX_MARKDOWN,
    PROFILE_DEVELOPMENT,
    PROFILE_PUBLIC,
    filter_commands_for_profile,
    filter_legacy_commands_for_profile,
    resolve_command_profile,
)
from pcobra.cobra.architecture.overview import USER_ROUTE_BACKEND_ENTRYPOINT
from pcobra.cobra.cli.plugin import (
    descubrir_plugins,
    configure_plugin_policy,
    PLUGINS_ALLOWLIST_ENV,
    PLUGINS_SAFE_MODE_ENV,
)
from pcobra.cobra.cli.utils import messages
from pcobra.cobra.cli.utils import config as config_module
from pcobra.cobra.cli.services.command_factory import (
    CommandClassRoute,
    build_command_from_route,
    load_command_class,
)
from pcobra.cobra.cli.utils.unicode_sanitize import sanitize_input
from pcobra.cobra.cli.utils.autocomplete import (
    autocomplete_available,
    directories_completer,
    enable_autocomplete,
    files_completer,
)

# Metadata injected at build time
CLI_VERSION = environ.get("COBRA_CLI_VERSION", "dev")
CLI_COMMIT = environ.get("COBRA_CLI_COMMIT", "unknown")
SQLITE_DB_KEY_ENV = "SQLITE_DB_KEY"
COBRA_DEV_MODE_ENV = "COBRA_DEV_MODE"
COBRA_DEV_EPHEMERAL_CONFIRM_ENV = "COBRA_DEV_ALLOW_EPHEMERAL_KEY"
COBRA_ALLOW_INSECURE_FALLBACK_ENV = "COBRA_ALLOW_INSECURE_FALLBACK"
COBRA_ALLOW_INSECURE_NON_INTERACTIVE_ENV = "COBRA_ALLOW_INSECURE_NON_INTERACTIVE"
COBRA_INTERNAL_ENABLE_CLI_V1_ENV = "COBRA_INTERNAL_ENABLE_CLI_V1"
COBRA_ENABLE_LEGACY_CLI_ENV = "COBRA_INTERNAL_ENABLE_LEGACY_CLI"
LANG_CHOICES = tuple(OFFICIAL_TRANSPILATION_TARGETS)
LEGACY_COMMAND_MIGRATION_MAP: dict[str, dict[str, str]] = {
    "ejecutar": {
        "target": "run",
        "hint": "cobra run <archivo.co>",
    },
    "compilar": {
        "target": "build",
        "hint": "cobra build <archivo.co>",
    },
    "verificar": {
        "target": "test",
        "hint": "cobra test <archivo.co>",
    },
    "modulos": {
        "target": "mod",
        "hint": "cobra mod <list|install|remove|publish|search>",
    },
}


class CliErrorYaMostrado(Exception):
    """Error de CLI cuya salida al usuario ya fue emitida por el comando."""

    error_ya_mostrado = True


class AppConfig:
    # Cargar configuración desde archivo
    try:
        config_data = config_module.load_config()
    except Exception as e:  # pragma: no cover - handled by tests
        logging.error(f"Failed to load configuration: {e}")
        config_data: Dict[str, str] = {}
    DEFAULT_LANGUAGE = config_data.get("language", "es")
    DEFAULT_COMMAND = config_data.get("default_command", "run")
    PROGRAM_NAME = config_data.get("program_name", "cobra")
    BASE_COMMAND_ROUTES: List[CommandClassRoute] = [
        CommandClassRoute("pcobra.cobra.cli.commands.interactive_cmd", "InteractiveCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.compile_cmd", "CompileCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.execute_cmd", "ExecuteCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.modules_cmd", "ModulesCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.dependencias_cmd", "DependenciasCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.docs_cmd", "DocsCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.empaquetar_cmd", "EmpaquetarCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.package_cmd", "PaqueteCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.crear_cmd", "CrearCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.init_cmd", "InitCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.jupyter_cmd", "JupyterCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.container_cmd", "ContainerCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.bench_cmd", "BenchCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.benchmarks_cmd", "BenchmarksCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.benchmarks2_cmd", "BenchmarksV2Command"),
        CommandClassRoute("pcobra.cobra.cli.commands.bench_transpilers_cmd", "BenchTranspilersCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.benchthreads_cmd", "BenchThreadsCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.profile_cmd", "ProfileCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.qualia_cmd", "QualiaCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.cache_cmd", "CacheCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.transpilar_inverso_cmd", "TranspilarInversoCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.verify_cmd", "VerifyCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.validar_sintaxis_cmd", "ValidarSintaxisCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.qa_validar_cmd", "QaValidarCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.plugins_cmd", "PluginsCommand"),
        CommandClassRoute("pcobra.cobra.cli.commands.agix_cmd", "AgixCommand"),
    ]
    # Compatibilidad para pruebas/consumidores legacy que parchean clases directas.
    BASE_COMMAND_CLASSES: List[Type[BaseCommand]] = []
    V2_COMMAND_ROUTES: List[CommandClassRoute] = [
        CommandClassRoute("pcobra.cobra.cli.commands_v2.run_cmd", "RunCommandV2"),
        CommandClassRoute("pcobra.cobra.cli.commands_v2.build_cmd", "BuildCommandV2"),
        CommandClassRoute("pcobra.cobra.cli.commands_v2.test_cmd", "TestCommandV2"),
        CommandClassRoute("pcobra.cobra.cli.commands_v2.mod_cmd", "ModCommandV2"),
    ]
    V2_COMMAND_CLASSES: List[Type[BaseCommand]] = []


class CommandRegistry:
    def __init__(self, interpreter: Optional[InterpretadorCobra] = None) -> None:
        self.commands: Dict[str, BaseCommand] = {}
        self.interpreter = interpreter
        self.default_command_name: Optional[str] = AppConfig.DEFAULT_COMMAND

    @staticmethod
    def _is_legacy_cli_enabled() -> bool:
        return environ.get(COBRA_ENABLE_LEGACY_CLI_ENV, "").strip() == "1"

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

    def _resolve_v2_command_routes(self, profile: str) -> List[CommandClassRoute]:
        if AppConfig.V2_COMMAND_CLASSES:
            routes = [
                CommandClassRoute(cls.__module__, cls.__name__)
                for cls in AppConfig.V2_COMMAND_CLASSES
            ]
        else:
            routes = list(AppConfig.V2_COMMAND_ROUTES)
        if profile == PROFILE_DEVELOPMENT and self._is_legacy_cli_enabled():
            routes.append(CommandClassRoute("pcobra.cobra.cli.commands_v2.legacy_cmd", "LegacyCommandGroupV2"))
            logging.getLogger(__name__).debug(
                "Compatibilidad legacy v2 habilitada por flag interno %s=1.",
                COBRA_ENABLE_LEGACY_CLI_ENV,
            )
        return routes

    def _resolve_v1_command_routes(self) -> List[CommandClassRoute]:
        """Carga comandos v1 y difiere imports GUI/opcionales hasta el registro."""
        if AppConfig.BASE_COMMAND_CLASSES:
            routes = [
                CommandClassRoute(cls.__module__, cls.__name__)
                for cls in AppConfig.BASE_COMMAND_CLASSES
            ]
        else:
            routes = list(AppConfig.BASE_COMMAND_ROUTES)
            routes.append(CommandClassRoute("pcobra.cobra.cli.commands.flet_cmd", "FletCommand"))
        return routes

    def register_base_commands(
        self,
        subparsers: Any,
        *,
        ui: str = "v2",
        profile: str = PROFILE_PUBLIC,
    ) -> Dict[str, BaseCommand]:
        base_commands = []
        ui_effective = ui
        if ui == "v2" and AppConfig.BASE_COMMAND_CLASSES:
            logging.getLogger(__name__).debug(
                "Compatibilidad tests/legacy: BASE_COMMAND_CLASSES detectado, usando rutas v1."
            )
            command_routes = self._resolve_v1_command_routes()
            ui_effective = "v1"
        else:
            command_routes = (
                self._resolve_v2_command_routes(profile)
                if ui == "v2"
                else self._resolve_v1_command_routes()
            )

        for route in command_routes:
            try:
                base_commands.append(
                    build_command_from_route(
                        route,
                        command_builder=self.create_command,
                    )
                )
            except TypeError as e:
                logging.error(
                    "Contrato inválido en comando %s.%s: %s. "
                    "Se omite el comando y la CLI continúa en modo degradado.",
                    route.module_path,
                    route.class_name,
                    e,
                )
            except Exception as e:
                logging.error(
                    "Failed to load/create command %s.%s: %s",
                    route.module_path,
                    route.class_name,
                    e,
                )
                continue

        plugin_commands = descubrir_plugins()
        all_commands = base_commands + plugin_commands

        if ui_effective == "v2":
            allowed_names = filter_commands_for_profile((cmd.name for cmd in all_commands), profile)
            all_commands = [cmd for cmd in all_commands if cmd.name in allowed_names]
            if profile == PROFILE_PUBLIC:
                logging.getLogger(__name__).debug(
                    "Perfil público activo: comandos expuestos=%s",
                    sorted(allowed_names),
                )
            elif profile == PROFILE_DEVELOPMENT:
                logging.getLogger(__name__).debug(
                    "Perfil desarrollo activo: comandos internos habilitados."
                )
        else:
            allowed_names = filter_legacy_commands_for_profile((cmd.name for cmd in all_commands), profile)
            all_commands = [cmd for cmd in all_commands if cmd.name in allowed_names]
            if profile == PROFILE_PUBLIC:
                logging.getLogger(__name__).debug(
                    "Perfil público en CLI v1: comandos legacy visibles=%s",
                    sorted(allowed_names),
                )
            elif profile == PROFILE_DEVELOPMENT:
                logging.getLogger(__name__).debug(
                    "Perfil desarrollo en CLI v1: comandos internos + obsoletos habilitados."
                )

        self.commands = {cmd.name: cmd for cmd in all_commands}

        for command in all_commands:
            try:
                command.register_subparser(subparsers)
            except Exception as e:
                logging.error(f"Failed to register subparser for {command.name}: {e}")
                del self.commands[command.name]

        return self.commands

    def get_default_command(self) -> Optional[BaseCommand]:
        return self.commands.get(self.default_command_name)

    def get_default_command_name(self) -> Optional[str]:
        return self.default_command_name


class CliApplication:
    """Aplicación principal de CLI con inicialización idempotente por instancia.

    Ciclo de vida esperado:
    1. `initialize()` construye recursos base una sola vez (parser, intérprete y registry).
    2. `_parse_arguments()` garantiza que la estructura de subcomandos exista y evita
       registrar subparsers/comandos más de una vez en la misma instancia.
    3. `run()` puede invocarse múltiples veces sobre la misma instancia sin conflictos
       de comandos por doble registro.
    4. `cleanup()` libera recursos al finalizar cada ejecución de `run()`.
    """

    def __init__(self) -> None:
        self.parser: Optional[CustomArgumentParser] = None
        self.interpreter: Optional[InterpretadorCobra] = None
        self.command_registry: Optional[CommandRegistry] = None
        self._subparsers: Optional[argparse._SubParsersAction] = None
        self._commands_registered = False
        self._selected_ui = "v2"

    @contextmanager
    def resource_management(self) -> ContextManager[None]:
        try:
            yield
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        if self.interpreter and hasattr(self.interpreter, "cleanup"):
            self.interpreter.cleanup()

    def initialize(self) -> None:
        if self.parser and self.command_registry and self.interpreter:
            return
        setup_gettext()
        self.interpreter = InterpretadorCobra()
        self.command_registry = CommandRegistry(self.interpreter)
        self.parser = self._build_argument_parser()

    def _ensure_command_structure(self) -> None:
        if not self.parser or not self.command_registry:
            raise RuntimeError("Application not properly initialized")
        if self._subparsers is None:
            self._subparsers = self.parser.add_subparsers(
                dest="command",
                parser_class=CustomArgumentParser,
            )
        if self._commands_registered:
            return

        command_profile = resolve_command_profile()
        selected_ui = getattr(self, "_selected_ui", "v2")
        self.command_registry.register_base_commands(
            self._subparsers,
            ui=selected_ui,
            profile=command_profile,
        )
        command_profile = resolve_command_profile()
        if command_profile != PROFILE_PUBLIC:
            menu_parser = self._subparsers.add_parser("menu", help=_("Modo interactivo"))
            menu_parser.set_defaults(cmd="menu")
        self._commands_registered = True

    def _normalizar_flags_sesion(self, args: argparse.Namespace) -> argparse.Namespace:
        """Normaliza aliases semánticos de sesión antes de resolver políticas."""
        if bool(getattr(args, "solo_cobra", False)):
            args.modo = "cobra"
        return args

    def _command_requires_sqlite_db_key(self, args: argparse.Namespace) -> bool:
        command = getattr(args, "cmd", None)
        if isinstance(command, BaseCommand):
            return bool(getattr(command, "requires_sqlite_key", False))
        return False

    def _is_enabled_env_flag(self, env_name: str) -> bool:
        return environ.get(env_name, "").strip() == "1"

    def _is_internal_v1_ui_enabled(self) -> bool:
        return (
            resolve_command_profile() == PROFILE_DEVELOPMENT
            and self._is_enabled_env_flag(COBRA_INTERNAL_ENABLE_CLI_V1_ENV)
        )

    def _ensure_sqlite_db_key(self, args: argparse.Namespace) -> None:
        command = getattr(args, "cmd", None)
        command_name = command.name if isinstance(command, BaseCommand) else _("desconocido")
        sqlite_db_key = (environ.get(SQLITE_DB_KEY_ENV) or "").strip()
        if sqlite_db_key:
            return

        dev_mode_enabled = self._is_enabled_env_flag(COBRA_DEV_MODE_ENV)
        dev_ephemeral_env_confirmation = self._is_enabled_env_flag(COBRA_DEV_EPHEMERAL_CONFIRM_ENV)
        dev_ephemeral_cli_confirmation = bool(getattr(args, "dev_ephemeral_key", False))

        if dev_mode_enabled and dev_ephemeral_env_confirmation and dev_ephemeral_cli_confirmation:
            environ[SQLITE_DB_KEY_ENV] = secrets.token_urlsafe(32)
            logging.getLogger(__name__).warning(
                "Modo desarrollo confirmado para comando '%s' (%s=1 + %s=1 + --dev-ephemeral-key): usando clave efímera local para %s.",
                command_name,
                COBRA_DEV_MODE_ENV,
                COBRA_DEV_EPHEMERAL_CONFIRM_ENV,
                SQLITE_DB_KEY_ENV,
            )
            return

        raise RuntimeError(
            f"Falta la variable de entorno 'SQLITE_DB_KEY' (clave requerida por comando '{command_name}'). "
            "Configúrala antes de iniciar la CLI (ejemplo: "
            "export SQLITE_DB_KEY='clave-segura'). Para pruebas locales "
            "controladas puedes habilitar una clave efímera solo si confirmas "
            f"explícitamente {COBRA_DEV_MODE_ENV}=1, "
            f"{COBRA_DEV_EPHEMERAL_CONFIRM_ENV}=1 y el flag --dev-ephemeral-key."
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
        parser.add_argument(
            "--format",
            "--formatear",
            dest="formatear",
            action="store_true",
            help=_("Format file before processing"),
        )
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
        parser.add_argument(
            "--allow-insecure-fallback",
            action="store_true",
            default=self._is_enabled_env_flag(COBRA_ALLOW_INSECURE_FALLBACK_ENV),
            help=_(
                "Permite explícitamente fallback inseguro de sandbox "
                "(solo para desarrollo controlado)."
            ),
        )
        parser.add_argument(
            "--allow-insecure-non-interactive",
            action="store_true",
            default=self._is_enabled_env_flag(COBRA_ALLOW_INSECURE_NON_INTERACTIVE_ENV),
            help=_(
                "Permite fallback inseguro en CI/no interactivo. "
                "Requiere --allow-insecure-fallback."
            ),
        )
        parser.add_argument(
            "--modo",
            choices=CLI_MODOS_PERMITIDOS,
            default=MODO_POR_DEFECTO,
            help=_(
                "Define el alcance de la sesión: "
                "cobra (solo programar/interpretar Cobra, sin codegen), "
                "transpilar (solo generar código), "
                "mixto (ejecutar y transpilar)."
            ),
        )
        parser.add_argument(
            "--solo-cobra",
            action="store_true",
            help=_(
                "Alias semántico de --modo cobra: sesión para solo programar/interpretar "
                "Cobra sin rutas de codegen."
            ),
        )
        ui_choices = ("v1", "v2") if self._is_internal_v1_ui_enabled() else ("v2",)
        parser.add_argument("--ui", choices=ui_choices, default="v2", help=argparse.SUPPRESS)
        parser.add_argument("--lang",
                          default=environ.get("COBRA_LANG", AppConfig.DEFAULT_LANGUAGE),
                          help=_("Interface language code"))
        parser.add_argument("--no-color", action="store_true",
                          help=_("Disable colored output"))
        parser.add_argument("--extra-validators",
                          help=_("Path to custom validators module"),
                          type=Path)
        parser.add_argument(
            "--legacy-imports",
            action="store_true",
            help=_("Habilita temporalmente imports legacy (cobra/core). Migre a pcobra.*"),
        )
        parser.add_argument(
            "--dev-ephemeral-key",
            action="store_true",
            help=_(
                "Confirma explícitamente (solo desarrollo local) el uso de una "
                "clave efímera para SQLITE_DB_KEY. Requiere COBRA_DEV_MODE=1 y "
                "COBRA_DEV_ALLOW_EPHEMERAL_KEY=1."
            ),
        )
        parser.add_argument(
            "--plugins-safe-mode",
            dest="plugins_safe_mode",
            action="store_true",
            help=_("Activa modo seguro de plugins (bloquea no permitidos)"),
        )
        parser.add_argument(
            "--plugins-unsafe-mode",
            dest="plugins_safe_mode",
            action="store_false",
            help=_("Desactiva modo seguro de plugins (permite cualquier plugin)"),
        )
        parser.add_argument(
            "--plugins-allowlist",
            dest="plugins_allowlist",
            default=environ.get(PLUGINS_ALLOWLIST_ENV, ""),
            help=_(
                "Lista permitida de plugins separados por coma (ruta exacta, "
                "módulo o prefix:/sha256:hash). También vía COBRA_PLUGINS_ALLOWLIST."
            ),
        )
        parser.set_defaults(
            plugins_safe_mode=environ.get(PLUGINS_SAFE_MODE_ENV, "1").strip().lower() in {"1", "true", "yes", "on"}
        )

    def _is_ci_context(self) -> bool:
        ci_markers = ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "JENKINS_URL", "BUILD_NUMBER")
        return any((environ.get(marker) or "").strip() for marker in ci_markers)

    def _is_non_interactive_context(self) -> bool:
        stdin_is_tty = bool(getattr(sys.stdin, "isatty", lambda: False)())
        stdout_is_tty = bool(getattr(sys.stdout, "isatty", lambda: False)())
        return not (stdin_is_tty and stdout_is_tty)

    def _registrar_advertencia_seguridad(
        self,
        *,
        event: str,
        command_name: str | None,
        reason: str,
        audit_id: str,
    ) -> None:
        message = (
            f"security_policy_warning event={event} command={command_name or 'unknown'} "
            f"reason={reason} audit_id={audit_id}"
        )
        logging.getLogger(__name__).warning(
            message,
            extra={
                "event": event,
                "command": command_name,
                "reason": reason,
                "audit_id": audit_id,
            },
        )

    def _enforce_runtime_safety_policy(self, args: argparse.Namespace) -> None:
        command_name = getattr(getattr(args, "cmd", None), "name", None)
        allow_insecure_fallback = bool(getattr(args, "allow_insecure_fallback", False))
        allow_insecure_non_interactive = bool(
            getattr(args, "allow_insecure_non_interactive", False)
        )

        if allow_insecure_non_interactive and not allow_insecure_fallback:
            self._registrar_advertencia_seguridad(
                event="invalid_non_interactive_override",
                command_name=command_name,
                reason="non_interactive_override_without_fallback",
                audit_id="SEC-RUNTIME-001",
            )
            raise RuntimeError(
                "--allow-insecure-non-interactive requiere "
                "--allow-insecure-fallback."
            )

        if not getattr(args, "seguro", True):
            self._registrar_advertencia_seguridad(
                event="unsafe_mode",
                command_name=command_name,
                reason="safe_mode_disabled",
                audit_id="SEC-RUNTIME-002",
            )

        if not allow_insecure_fallback:
            return

        self._registrar_advertencia_seguridad(
            event="insecure_fallback",
            command_name=command_name,
            reason="explicit_allow_insecure_fallback",
            audit_id="SEC-RUNTIME-003",
        )
        messages.mostrar_advertencia(
            _(
                "Fallback inseguro habilitado explícitamente. "
                "Úselo solo en desarrollo controlado."
            )
        )

        if (self._is_ci_context() or self._is_non_interactive_context()) and not allow_insecure_non_interactive:
            self._registrar_advertencia_seguridad(
                event="blocked_insecure_fallback_non_interactive",
                command_name=command_name,
                reason="missing_non_interactive_override",
                audit_id="SEC-RUNTIME-004",
            )
            raise RuntimeError(
                "Fallback inseguro bloqueado en contexto CI/no interactivo. "
                "Use --allow-insecure-non-interactive para override explícito."
            )

        if allow_insecure_non_interactive:
            self._registrar_advertencia_seguridad(
                event="insecure_fallback_non_interactive_override",
                command_name=command_name,
                reason="explicit_non_interactive_override",
                audit_id="SEC-RUNTIME-005",
            )
            messages.mostrar_advertencia(
                _(
                    "Override explícito activo: fallback inseguro permitido en "
                    "contexto CI/no interactivo."
                )
            )

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
            description=_(
                "CLI de Cobra para ejecutar e interpretar scripts, "
                "transpilar código a otros lenguajes o usar ambos flujos "
                "según --modo (cobra, transpilar, mixto). "
                "Modo cobra = solo programar/interpretar Cobra sin codegen."
            ),
            epilog=_(
                "Ejemplos públicos:\n"
                "  cobra run <archivo.co>\n"
                "  cobra build <archivo.co>\n"
                "  cobra test <archivo.co>\n"
                "  cobra mod <list|install|remove|publish|search>"
            ),
        )
        self._configure_cli_options(parser)
        return parser

    def _parse_arguments(self, argv: List[str]) -> argparse.Namespace:
        if not self.parser or not self.command_registry:
            raise RuntimeError("Application not properly initialized")

        self._selected_ui = self._resolve_selected_ui_from_argv(argv)
        if any(token in {"-h", "--help", "--ayuda"} for token in argv):
            configure_plugin_policy(safe_mode=True, allowlist="")
            self._ensure_command_structure()
            if autocomplete_available():
                self._configure_autocomplete(self.parser)
                enable_autocomplete(self.parser)
            return self._normalizar_flags_sesion(self.parser.parse_args(argv))

        preliminary_args, _ = self.parser.parse_known_args(argv)
        preliminary_args = self._normalizar_flags_sesion(preliminary_args)
        configure_plugin_policy(
            safe_mode=getattr(preliminary_args, "plugins_safe_mode", True),
            allowlist=getattr(preliminary_args, "plugins_allowlist", ""),
        )
        self._ensure_command_structure()

        if autocomplete_available():
            self._configure_autocomplete(self.parser)
            enable_autocomplete(self.parser)
        else:
            logging.getLogger(__name__).debug(
                "Autocompletado deshabilitado: argcomplete no está instalado.",
            )

        parsed = self.parser.parse_args(argv)
        return self._normalizar_flags_sesion(parsed)

    def _enforce_public_startup_guard(self) -> None:
        """Bloquea exposición accidental de rutas legacy en perfil público."""
        command_profile = resolve_command_profile()
        selected_ui = getattr(self, "_selected_ui", "v2")
        if command_profile != PROFILE_PUBLIC:
            return

        blocked_routes: list[str] = []
        if self.command_registry and self.command_registry._is_legacy_cli_enabled():
            blocked_routes.append(f"legacy command group ({COBRA_ENABLE_LEGACY_CLI_ENV}=1)")
        if is_internal_legacy_targets_enabled():
            blocked_routes.append(f"legacy targets ({LEGACY_BACKENDS_FEATURE_FLAG}=1)")

        if not blocked_routes:
            return

        raise RuntimeError(
            "Perfil público bloqueado por rutas legacy/internal migration only: "
            f"{', '.join(blocked_routes)}. "
            "Use CLI v2 pública (run/build/test/mod) y enrute por "
            f"{USER_ROUTE_BACKEND_ENTRYPOINT}."
        )

    @staticmethod
    def _first_non_option_token_index(argv: list[str]) -> Optional[int]:
        for index, token in enumerate(argv):
            if token == "--":
                return index + 1 if index + 1 < len(argv) else None
            if not token.startswith("-"):
                return index
        return None

    def _apply_public_cli_policy(self, argv: list[str]) -> list[str]:
        """Fuerza UI v2 para usuarios y migra comandos legacy automáticamente."""
        normalized = list(argv)
        profile = resolve_command_profile()
        if profile != PROFILE_PUBLIC:
            return normalized

        if self._resolve_selected_ui_from_argv(normalized) == "v1":
            for index, token in enumerate(normalized):
                if token == "--ui" and index + 1 < len(normalized):
                    normalized[index + 1] = "v2"
            messages.mostrar_advertencia(
                _(
                    "CLI v1 está reservada para desarrollo interno. "
                    "Se aplicó migración automática a UI v2 pública."
                )
            )

        command_idx = self._first_non_option_token_index(normalized)
        if command_idx is None:
            return normalized

        command_token = normalized[command_idx].strip().lower()
        migration = LEGACY_COMMAND_MIGRATION_MAP.get(command_token)
        if not migration:
            return normalized

        migrated_to = migration["target"]
        normalized[command_idx] = migrated_to
        messages.mostrar_advertencia(
            _(
                "Comando legacy '{legacy}' detectado fuera de entorno interno. "
                "Migración automática aplicada: use '{current}'. "
                "Sugerencia: {hint}."
            ).format(
                legacy=command_token,
                current=migrated_to,
                hint=migration["hint"],
            )
        )
        logging.getLogger(__name__).warning(
            "legacy_command_auto_migrated legacy=%s target=%s profile=%s matrix=%s",
            command_token,
            migrated_to,
            profile,
            COMMAND_VISIBILITY_MATRIX_MARKDOWN.replace("\n", " | "),
        )
        return normalized

    @staticmethod
    def _resolve_ui_token_from_argv(argv: list[str]) -> str:
        for index, token in enumerate(argv):
            if token == "--ui" and index + 1 < len(argv):
                return argv[index + 1].strip().lower()
        return "v2"

    def _resolve_selected_ui_from_argv(self, argv: list[str]) -> str:
        requested_ui = self._resolve_ui_token_from_argv(argv)
        if requested_ui != "v1":
            return "v2"
        if self._is_internal_v1_ui_enabled():
            return "v1"
        messages.mostrar_advertencia(
            _(
                "UI v1 está deshabilitada para uso público. "
                "Se mantiene UI v2 (cobra run/build/test/mod)."
            )
        )
        return "v2"

    @staticmethod
    def _resolve_reverse_transpile_choices() -> tuple[tuple[str, ...], tuple[str, ...]]:
        try:
            module = __import__(
                "pcobra.cobra.cli.commands.transpilar_inverso_cmd",
                fromlist=["ORIGIN_CHOICES", "DESTINO_CHOICES"],
            )
            origin_choices = tuple(getattr(module, "ORIGIN_CHOICES", ()))
            destino_choices = tuple(getattr(module, "DESTINO_CHOICES", ()))
            return origin_choices, destino_choices
        except Exception as exc:
            logging.getLogger(__name__).error(
                "No se pudieron resolver opciones de transpilar inverso: %s", exc
            )
            return tuple(), tuple()

    def _handle_execution_error(self, exc: Exception, language: str, debug_activo: bool = False) -> int:
        error_ya_mostrado = isinstance(exc, CliErrorYaMostrado) or bool(
            getattr(exc, "error_ya_mostrado", False)
        )
        mensaje = str(exc).strip() or _("Ha ocurrido un error inesperado.")

        if not error_ya_mostrado:
            messages.mostrar_error(mensaje, registrar_log=False)

        if debug_activo:
            logging.exception("Error in execution")
            logging.getLogger(__name__).debug(format_traceback(exc, language))
        return 1

    @staticmethod
    def _sanear_texto_entrada(value: object) -> str:
        if isinstance(value, str):
            return sanitize_input(value)
        if value is None:
            return ""
        return sanitize_input(str(value))

    def _sanear_argv(self, argv: List[str]) -> List[str]:
        return [self._sanear_texto_entrada(token) for token in argv]

    def _leer_input_seguro(self, prompt: str) -> Optional[str]:
        try:
            return self._sanear_texto_entrada(input(prompt))
        except EOFError:
            messages.mostrar_info(_("Entrada finalizada (EOF). Cancelando menú interactivo."))
            return None
        except KeyboardInterrupt:
            messages.mostrar_info(_("\nInterrupción detectada. Cancelando menú interactivo."))
            return None

    def _leer_opcion_validada(
        self,
        prompt: str,
        opciones_validas: tuple[str, ...] | list[str],
        campo: str,
        max_intentos: int = 3,
    ) -> tuple[Optional[str], int]:
        opciones_normalizadas = tuple(opcion.strip().lower() for opcion in opciones_validas)
        opciones_mostrables = ", ".join(opciones_normalizadas)

        for intento in range(max_intentos):
            valor = self._leer_input_seguro(prompt)
            if valor is None:
                return None, 0

            valor = self._sanear_texto_entrada(valor)
            valor_normalizado = valor.strip().lower()
            if valor_normalizado in opciones_normalizadas:
                return valor_normalizado, 0

            restantes = max_intentos - intento - 1
            messages.mostrar_error(
                _(
                    "Valor inválido para {campo}: '{valor}'. Opciones válidas: {opciones}."
                ).format(
                    campo=campo,
                    valor=valor.strip(),
                    opciones=opciones_mostrables,
                ),
                registrar_log=False,
            )
            if restantes > 0:
                messages.mostrar_info(
                    _("Intente nuevamente. Intentos restantes: {}.").format(restantes)
                )

        messages.mostrar_error(
            _(
                "Demasiados intentos inválidos para {campo}. Finalizando menú interactivo."
            ).format(campo=campo),
            registrar_log=False,
        )
        return None, 1

    def run_menu(self, parsed_args: argparse.Namespace) -> int:
        if not self.command_registry:
            raise RuntimeError("Command registry not initialized")
        if not sys.stdin.isatty():
            messages.mostrar_error(
                _("El menú interactivo requiere una terminal (TTY). Ejecuta un comando directo."),
                registrar_log=False,
            )
            return 1
        modo = str(getattr(parsed_args, "modo", MODO_POR_DEFECTO)).strip().lower()

        def _accion_permitida(comando: str) -> bool:
            try:
                capability = "execute" if comando == "ejecutar" else "codegen"
                validar_politica_modo(comando, parsed_args, capability=capability)
                return True
            except ValueError:
                return False

        acciones: list[tuple[str, str]] = []
        if _accion_permitida("ejecutar"):
            acciones.append(("ejecutar", _("Ejecutar/interpretar script Cobra")))
        if _accion_permitida("compilar"):
            acciones.append(("transpilar", _("Transpilar/generar código")))

        if not acciones:
            messages.mostrar_error(
                _("No hay acciones disponibles para --modo {}.").format(modo),
                registrar_log=False,
            )
            return 1

        if len(acciones) == 1:
            accion = acciones[0][0]
            messages.mostrar_info(
                _("Modo {modo} activo: menú limitado a '{accion}'.").format(
                    modo=modo, accion=accion
                )
            )
            if modo == "cobra" and accion == "ejecutar":
                messages.mostrar_info(
                    _("Modo cobra: flujo directo de ejecutar (sin prompts de transpilación).")
                )
        else:
            print(_("Seleccione una acción:"))
            for idx, (nombre_accion, descripcion) in enumerate(acciones, start=1):
                print(f"{idx}. {descripcion}")
            opciones_validas = tuple(str(i) for i in range(1, len(acciones) + 1))
            seleccion, exit_code = self._leer_opcion_validada(
                _("Opción: "),
                opciones_validas,
                "acción",
            )
            if seleccion is None:
                return exit_code
            accion = acciones[int(seleccion) - 1][0]

        if accion == "ejecutar":
            archivo = self._leer_input_seguro(_("Ruta al archivo Cobra: "))
            if archivo is None:
                return 0
            ejecutar_cmd = self.command_registry.commands.get("ejecutar")
            if not ejecutar_cmd:
                messages.mostrar_error(_("Comando 'ejecutar' no disponible"), registrar_log=False)
                return 1
            command_args = argparse.Namespace(
                archivo=archivo.strip(),
                sandbox=getattr(parsed_args, "seguro", True),
                contenedor=None,
                depurar=getattr(parsed_args, "debug", False),
                formatear=getattr(parsed_args, "formatear", False),
                modo=getattr(parsed_args, "modo", MODO_POR_DEFECTO),
            )
            return ejecutar_cmd.run(command_args)

        print(_("Lenguajes destino disponibles:"))
        print(", ".join(LANG_CHOICES))
        origin_choices, reverse_destino_choices = self._resolve_reverse_transpile_choices()
        if not origin_choices or not reverse_destino_choices:
            messages.mostrar_error(
                _("Comando 'transpilar-inverso' no disponible: contrato de opciones inválido."),
                registrar_log=False,
            )
            return 1
        print(_("Lenguajes de origen disponibles:"))
        print(", ".join(origin_choices))

        transpilar_desde_cobra = self._leer_input_seguro(_("¿Transpilar desde Cobra a otro lenguaje? (s/n): "))
        if transpilar_desde_cobra is None:
            return 0

        if transpilar_desde_cobra.strip().lower().startswith("s"):
            archivo = self._leer_input_seguro(_("Ruta al archivo Cobra: "))
            if archivo is None:
                return 0
            destino, exit_code = self._leer_opcion_validada(
                _("Lenguaje destino: "),
                LANG_CHOICES,
                "destino",
            )
            if destino is None:
                return exit_code
            archivo = archivo.strip()
            command_args = argparse.Namespace(
                archivo=archivo,
                tipo=destino,
                backend=None,
                tipos=None,
                modo=getattr(parsed_args, "modo", MODO_POR_DEFECTO),
            )
            compile_cmd = self.command_registry.commands.get("compilar")
            if not compile_cmd:
                messages.mostrar_error(_("Comando 'compilar' no disponible"), registrar_log=False)
                return 1
            return compile_cmd.run(command_args)
        else:
            archivo = self._leer_input_seguro(_("Ruta al archivo origen: "))
            if archivo is None:
                return 0
            origen, exit_code = self._leer_opcion_validada(
                _("Lenguaje origen: "),
                origin_choices,
                "origen",
            )
            if origen is None:
                return exit_code
            destino, exit_code = self._leer_opcion_validada(
                _("Lenguaje destino: "),
                reverse_destino_choices,
                "destino",
            )
            if destino is None:
                return exit_code
            archivo = archivo.strip()
            inv_cmd = self.command_registry.commands.get("transpilar-inverso")
            if not inv_cmd:
                messages.mostrar_error(_("Comando 'transpilar-inverso' no disponible"), registrar_log=False)
                return 1
            command_args = argparse.Namespace(
                archivo=archivo,
                origen=origen,
                destino=destino,
                modo=getattr(parsed_args, "modo", MODO_POR_DEFECTO),
            )
            return inv_cmd.run(command_args)

    def execute_command(self, args: argparse.Namespace, debug_activo: bool = False) -> int:
        """Ejecuta el comando resuelto desde ``args``.

        Pre-requisito recomendado: llamar a ``initialize()`` (o ``run()``) antes de
        invocar este método, para asegurar que parser y registry estén listos.
        Aun así, si el parser no existe en un estado parcial, devuelve un error
        controlado en lugar de propagar ``AttributeError``.
        """
        if not self.command_registry:
            raise RuntimeError("Command registry not initialized")
            
        command = getattr(args, "cmd", None)
        if command == "menu":
            return self.run_menu(args)
        if not command:
            if self.parser is not None:
                self.parser.print_help()
                return 1
            messages.mostrar_error(
                _("CLI no inicializada completamente: parser no disponible. "
                  "Ejecute initialize() antes de execute_command()."),
                registrar_log=False,
            )
            return 1
            
        try:
            result = command.run(args)
            return 0 if result is None else result
        except Exception as exc:
            return self._handle_execution_error(exc, args.lang, debug_activo)

    def run(self, argv: Optional[List[str]] = None) -> int:
        with self.resource_management():
            self.initialize()
            debug_activo = False
            if argv is None:
                argv = sys.argv[1:]
                if "PYTEST_CURRENT_TEST" in environ and not argv:
                    argv = []

            try:
                argv = self._sanear_argv(argv)
                argv = self._apply_public_cli_policy(argv)
                self._selected_ui = self._resolve_selected_ui_from_argv(argv)
                self._enforce_public_startup_guard()
                args = self._parse_arguments(argv)
                command = getattr(args, "cmd", None)
                command_name = command.name if isinstance(command, BaseCommand) else _("desconocido")
                if self._command_requires_sqlite_db_key(args):
                    self._ensure_sqlite_db_key(args)
                else:
                    logging.getLogger(__name__).info(
                        "SQLITE_DB_KEY no requerida por comando '%s'.", command_name
                    )
                self._enforce_runtime_safety_policy(args)
                debug_activo = bool(args.debug)
                setup_gettext(args.lang)
                messages.disable_colors(args.no_color)
                if getattr(args, "legacy_imports", False):
                    os.environ["PCOBRA_ENABLE_LEGACY_IMPORTS"] = "1"
                    messages.mostrar_info(
                        "Compatibilidad legacy habilitada para esta ejecución. "
                        "Actualiza tus imports a `pcobra.*` antes de fase 3."
                    )
                messages.mostrar_logo()

                return self.execute_command(args, debug_activo=debug_activo)
            except Exception as e:
                if debug_activo:
                    logging.exception("Fatal error in application")
                mensaje_error = str(e).strip() or _("Ha ocurrido un error inesperado.")
                messages.mostrar_error(
                    _("Fatal error: {}").format(mensaje_error),
                    registrar_log=False,
                )
                return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    configure_encoding()
    application = CliApplication()
    return application.run(argv)


def __getattr__(name: str):
    """Compatibilidad legacy para tests/consumidores que importan clases desde este módulo."""
    if name == "InteractiveCommand":
        return load_command_class(
            "pcobra.cobra.cli.commands.interactive_cmd",
            "InteractiveCommand",
        )
    raise AttributeError(name)


def configure_encoding() -> None:
    import os
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    os.environ["PYTHONIOENCODING"] = "utf-8"


if __name__ == "__main__":
    sys.exit(main())


import sys as _sys

_sys.modules.setdefault("cobra.cli.cli", _sys.modules[__name__])
