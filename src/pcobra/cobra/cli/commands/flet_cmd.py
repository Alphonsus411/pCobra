from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error


class FletCommand(BaseCommand):
    """Inicia el entorno IDLE basado en Flet."""
    name = "gui"

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
        try:
            import flet as flet_runtime
        except ModuleNotFoundError as e:
            missing_module = e.name or "desconocido"
            if missing_module == "flet":
                mostrar_error(_("Falta la dependencia 'flet'. Ejecuta: pip install flet."))
            else:
                mostrar_error(
                    _(
                        "Falta una dependencia requerida para iniciar GUI: '{0}'. "
                        "Verifica la instalación de dependencias de core/transpiladores."
                    ).format(missing_module)
                )
            return 1

        ui_target = getattr(args, "ui", "idle")
        gui_module = "pcobra.gui.idle" if ui_target == "idle" else "pcobra.gui.app"

        try:
            if ui_target == "idle":
                from pcobra.gui.idle import main
            else:
                from pcobra.gui.app import main
        except ModuleNotFoundError as e:
            missing_module = e.name or "desconocido"
            if missing_module == "flet":
                mostrar_error(_("Falta la dependencia 'flet'. Ejecuta: pip install flet."))
            else:
                mostrar_error(
                    _(
                        "No se pudo cargar la GUI ({0}) porque falta el módulo '{1}'. "
                        "Verifica dependencias de core/transpiladores."
                    ).format(gui_module, missing_module)
                )
            return 1
        except ImportError as e:
            mostrar_error(
                _("Error interno de importación en la GUI ({0}): {1}").format(gui_module, str(e))
            )
            return 1
        
        try:
            flet_runtime.app(target=main)
            return 0
        except Exception as e:
            mostrar_error(_("Error inesperado al ejecutar la aplicación: {0}").format(str(e)))
            return 1
