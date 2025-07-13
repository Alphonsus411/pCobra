from datetime import datetime
from cli.plugin import PluginCommand

class HoraCommand(PluginCommand):
    """Muestra la hora actual por pantalla."""

    name = "hora"
    version = "1.0"
    author = "Equipo Cobra"
    description = "Imprime la hora actual"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.description)
        parser.set_defaults(cmd=self)

    def run(self, args):
        ahora = datetime.now().strftime("%H:%M:%S")
        print(f"Hora actual: {ahora}")
