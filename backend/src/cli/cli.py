import argparse
import logging
import os
import sys

from .commands.compile_cmd import CompileCommand
from .commands.docs_cmd import DocsCommand
from .commands.execute_cmd import ExecuteCommand
from .commands.interactive_cmd import InteractiveCommand
from .commands.modules_cmd import ModulesCommand
from .commands.dependencias_cmd import DependenciasCommand

# La configuración de logging solo debe activarse cuando la CLI se ejecuta
# directamente para evitar modificar la configuración global al importar este
# módulo desde las pruebas u otros paquetes.


def main(argv=None):
    """Punto de entrada principal de la CLI."""
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(prog="cobra", description="CLI para Cobra")
    parser.add_argument("--formatear", action="store_true", help="Formatea el archivo antes de procesarlo")
    parser.add_argument("--depurar", action="store_true", help="Muestra mensajes de depuración")
    parser.add_argument("--seguro", action="store_true", help="Ejecuta en modo seguro")

    subparsers = parser.add_subparsers(dest="comando")

    comandos = [
        CompileCommand(),
        ExecuteCommand(),
        ModulesCommand(),
        DependenciasCommand(),
        DocsCommand(),
        InteractiveCommand(),
    ]

    command_map = {}
    for cmd in comandos:
        cmd.register_subparser(subparsers)
        command_map[cmd.name] = cmd

    parser.set_defaults(cmd=command_map["interactive"])

    if argv is None:
        if "PYTEST_CURRENT_TEST" in os.environ:
            argv = []
        else:
            argv = sys.argv[1:]

    args = parser.parse_args(argv)
    command = getattr(args, "cmd", command_map["interactive"])
    resultado = command.run(args)
    return 0 if resultado is None else resultado


if __name__ == "__main__":
    sys.exit(main())
