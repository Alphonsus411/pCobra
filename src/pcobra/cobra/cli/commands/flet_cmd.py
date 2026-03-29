import importlib
import re
from types import ModuleType
from typing import Any, Callable

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error


class FletCommand(BaseCommand):
    """Inicia el entorno IDLE basado en Flet."""
    name = "gui"
    requires_sqlite_key: bool = False
    _CRITICAL_GUI_MODULES = (
        "pcobra.cobra.cli.commands.compile_cmd",
        "pcobra.cobra.core",
        "pcobra.cobra.transpilers.target_utils",
        "pcobra.cobra.transpilers.targets",
        "pcobra.core.interpreter",
    )
    _CRITICAL_GUI_SYMBOLS = {
        "pcobra.cobra.core": ("Lexer", "Parser"),
        "pcobra.core.interpreter": ("InterpretadorCobra",),
        "pcobra.cobra.cli.commands.compile_cmd": ("TRANSPILERS",),
        "pcobra.cobra.transpilers.target_utils": ("target_cli_choices",),
    }

    def __init__(self) -> None:
        """Inicializa el comando."""
        super().__init__()

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            El parser configurado para este subcomando
        """
        parser = subparsers.add_parser(self.name, help=_("Inicia la interfaz gráfica"))
        parser.add_argument(
            "--ui",
            choices=("idle", "app"),
            default="idle",
            help=_("Selecciona la UI a iniciar: 'idle' (por defecto) o 'app'."),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la ejecución fue exitosa, 1 en caso de error
            
        Raises:
            ModuleNotFoundError: Si Flet no está instalado o falta un módulo GUI
        """
        ui_target = getattr(args, "ui", "idle")
        gui_module = "pcobra.gui.idle" if ui_target == "idle" else "pcobra.gui.app"

        try:
            import flet as flet_runtime
        except (ImportError, ModuleNotFoundError) as exc:
            self._report_import_error(exc, context="flet")
            return 1

        try:
            main = self._preflight_gui(gui_module)
        except ModuleNotFoundError as e:
            self._report_import_error(e, context=gui_module)
            return 1
        except ImportError as e:
            self._report_import_error(e, context=gui_module)
            return 1
        try:
            flet_runtime.app(target=main)
            return 0
        except Exception as e:
            mostrar_error(_("Error inesperado al ejecutar la aplicación: {0}").format(str(e)))
            return 1

    def _preflight_gui(self, gui_module: str) -> Callable[..., Any]:
        """Valida dependencias críticas de GUI/core antes de iniciar Flet."""
        for module_name in self._CRITICAL_GUI_MODULES:
            module = importlib.import_module(module_name)
            self._validate_required_symbols(module_name, module)

        gui = importlib.import_module(gui_module)
        return self._get_main(gui)

    def _validate_required_symbols(self, module_name: str, module: ModuleType) -> None:
        """Valida símbolos requeridos en módulos críticos para GUI."""
        for symbol in self._CRITICAL_GUI_SYMBOLS.get(module_name, ()):
            if not hasattr(module, symbol):
                raise ImportError(
                    f"missing symbol '{symbol}' in module '{module_name}'"
                )

    def _get_main(self, gui: ModuleType) -> Callable[..., Any]:
        if not hasattr(gui, "main"):
            raise ImportError(f"missing symbol 'main' in module '{gui.__name__}'")
        main = getattr(gui, "main")
        if not callable(main):
            raise ImportError(f"symbol 'main' in module '{gui.__name__}' is not callable")
        return main

    def _report_import_error(self, exc: ImportError, context: str) -> None:
        detail = str(exc) or repr(exc)
        missing_target, action = self._parse_missing_target(exc, detail)

        mostrar_error(
            _(
                "Error de importación GUI en '{0}': faltante detectado '{1}'. "
                "Detalle: {2}. Acción sugerida: {3}"
            ).format(context, missing_target, detail, action)
        )

    def _parse_missing_target(self, exc: ImportError, detail: str) -> tuple[str, str]:
        if isinstance(exc, ModuleNotFoundError):
            missing_module = self._extract_module_from_exception(exc, detail)
            return missing_module, self._dependency_action(missing_module)

        custom_symbol_match = re.search(r"missing symbol '([^']+)' in module '([^']+)'", detail)
        if custom_symbol_match:
            symbol_name, module_name = custom_symbol_match.groups()
            target = f"{module_name}.{symbol_name}"
            return target, self._local_import_action(module_name, symbol_name)

        not_callable_match = re.search(
            r"symbol '([^']+)' in module '([^']+)' is not callable", detail
        )
        if not_callable_match:
            symbol_name, module_name = not_callable_match.groups()
            target = f"{module_name}.{symbol_name}"
            return target, self._local_import_action(module_name, symbol_name, callable_required=True)

        cannot_import_match = re.search(r"cannot import name '([^']+)' from '([^']+)'", detail)
        if cannot_import_match:
            symbol_name, module_name = cannot_import_match.groups()
            target = f"{module_name}.{symbol_name}"
            return target, self._local_import_action(module_name, symbol_name)

        missing_module = self._extract_module_from_exception(exc, detail)
        return missing_module, self._dependency_action(missing_module)

    def _extract_module_from_exception(self, exc: ImportError, detail: str) -> str:
        missing_module = getattr(exc, "name", None)
        if missing_module:
            return missing_module

        patterns = (
            r"No module named '([^']+)'",
            r"No module named ([^\s]+)",
            r"cannot import name '[^']+' from '([^']+)'",
        )
        for pattern in patterns:
            match = re.search(pattern, detail)
            if match:
                return match.group(1)
        return "desconocido"

    def _dependency_action(self, missing_module: str) -> str:
        if missing_module == "flet":
            return "instala la dependencia faltante con 'pip install flet'."
        if missing_module.startswith("pcobra."):
            return (
                "corrige el import local y verifica que el módulo exista; "
                "si hace falta reinstala con 'pip install -e .'."
            )
        return f"instala la dependencia que provee '{missing_module}' o ajusta el import local."

    def _local_import_action(
        self,
        module_name: str,
        symbol_name: str,
        callable_required: bool = False,
    ) -> str:
        if callable_required:
            return (
                f"corrige el import local para que '{module_name}.{symbol_name}' sea invocable."
            )
        return f"corrige el import local de '{module_name}.{symbol_name}' o actualiza la dependencia que lo expone."
