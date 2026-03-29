import importlib
from types import ModuleType
from typing import Any, Callable

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error


class FletCommand(BaseCommand):
    """Inicia el entorno IDLE basado en Flet."""
    name = "gui"
    _CRITICAL_GUI_MODULES = (
        "pcobra.cobra.core",
        "pcobra.cobra.transpilers.target_utils",
        "pcobra.cobra.transpilers.targets",
    )

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
        except AttributeError:
            mostrar_error(
                _(
                    "Error de preflight GUI en '{0}': no existe función 'main'. "
                    "Acción: verifica la instalación/versión del paquete."
                ).format(gui_module)
            )
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
            importlib.import_module(module_name)

        gui = importlib.import_module(gui_module)
        return self._get_main(gui)

    def _get_main(self, gui: ModuleType) -> Callable[..., Any]:
        main = getattr(gui, "main")
        if not callable(main):
            raise AttributeError("main")
        return main

    def _report_import_error(self, exc: ImportError, context: str) -> None:
        missing_module = getattr(exc, "name", None) or "desconocido"
        if missing_module == "flet":
            mostrar_error(
                _(
                    "Error de dependencias GUI en '{0}': falta el módulo '{1}'. "
                    "Acción: pip install flet"
                ).format(context, missing_module)
            )
            return

        if missing_module.startswith("pcobra.cobra.core") or missing_module.startswith(
            "pcobra.cobra.transpilers"
        ):
            mostrar_error(
                _(
                    "Error de dependencias GUI en '{0}': falta el módulo crítico '{1}'. "
                    "Acción: pip install -e ."
                ).format(context, missing_module)
            )
            return

        detail = str(exc) or repr(exc)
        if isinstance(exc, ModuleNotFoundError):
            mostrar_error(
                _(
                    "Error interno de importación en '{0}': falta '{1}'. "
                    "Detalle: {2}. Acción: verifica/importa dependencias del módulo faltante."
                ).format(context, missing_module, detail)
            )
            return

        mostrar_error(
            _(
                "Error interno de importación en '{0}': {1}. "
                "Acción: revisa el traceback o reinstala el paquete."
            ).format(context, detail)
        )
