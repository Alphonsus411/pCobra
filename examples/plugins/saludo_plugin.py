from cli.plugin import PluginCommand

class SaludoCommand(PluginCommand):
    """Comando de ejemplo que imprime un saludo."""

    name = "saludo"
    version = "1.0"
    author = "Equipo Cobra"
    description = "Comando de saludo de ejemplo"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Muestra un saludo")
        parser.set_defaults(cmd=self)

    def run(self, args):
        print("¡Hola desde el plugin de ejemplo!")
