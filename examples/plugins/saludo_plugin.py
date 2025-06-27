from src.cli.plugin_loader import PluginCommand

class SaludoCommand(PluginCommand):
    """Comando de ejemplo que imprime un saludo."""

    name = "saludo"
    version = "1.0"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Muestra un saludo")
        parser.set_defaults(cmd=self)

    def run(self, args):
        print("¡Hola desde el plugin de ejemplo!")
