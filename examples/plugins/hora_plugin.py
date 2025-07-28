from datetime import datetime, timezone

from cobra.cli.plugin import PluginCommand


class HoraCommand(PluginCommand):
    """Muestra la hora actual por pantalla."""
    name = "hora"
    version = "1.0"
    author = "Equipo Cobra"
    description = "Imprime la hora actual"

    def register_subparser(self, subparsers):
        """Registra el subparser para el comando hora.
        
        Args:
            subparsers: Objeto subparsers donde registrar el comando
        """
        parser = subparsers.add_parser(self.name, help=self.description)
        parser.set_defaults(cmd=self)

    def run(self, args):
        """Ejecuta el comando para mostrar la hora.
        
        Args:
            args: Argumentos parseados del comando
        
        Returns:
            None
        """
        try:
            ahora = datetime.now(tz=timezone.utc).strftime("%H:%M:%S")
            print(f"Hora actual (UTC): {ahora}")
        except Exception as e:
            print(f"Error al obtener la hora: {e}")