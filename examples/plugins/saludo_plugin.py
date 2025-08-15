from argparse import ArgumentParser
from typing import Any
from cobra.cli.plugin import PluginCommand

class SaludoCommand(PluginCommand):
    """Comando de ejemplo que imprime un saludo."""
    name = "saludo"
    version = "1.0"
    author = "Equipo Cobra"
    description = "Comando de saludo de ejemplo"
    
    def register_subparser(self, subparsers: Any) -> None:
        parser = subparsers.add_parser(self.name, help="Muestra un saludo")
        parser.set_defaults(cmd=self)
        
    def run(self, args: Any) -> int:
        print("¡Hola desde el plugin de ejemplo!")
        return 0