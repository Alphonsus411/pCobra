import argparse
import logging
import os
import sys

from .i18n import _, setup_gettext

from .commands.compile_cmd import CompileCommand
from .commands.docs_cmd import DocsCommand
from .commands.execute_cmd import ExecuteCommand
from .commands.interactive_cmd import InteractiveCommand
from .commands.jupyter_cmd import JupyterCommand
from .commands.flet_cmd import FletCommand
from .commands.agix_cmd import AgixCommand
from .plugin_loader import descubrir_plugins
from .commands.plugins_cmd import PluginsCommand
from .commands.modules_cmd import ModulesCommand
from .commands.dependencias_cmd import DependenciasCommand
from .commands.empaquetar_cmd import EmpaquetarCommand
from .commands.crear_cmd import CrearCommand
from .commands.init_cmd import InitCommand

# La configuración de logging solo debe activarse cuando la CLI se ejecuta
# directamente para evitar modificar la configuración global al importar este
# módulo desde las pruebas u otros paquetes.


def main(argv=None):
    """Punto de entrada principal de la CLI."""
    setup_gettext()
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(prog="cobra", description=_("CLI para Cobra"))
    parser.add_argument("--formatear", action="store_true", help=_("Formatea el archivo antes de procesarlo"))
    parser.add_argument("--depurar", action="store_true", help=_("Muestra mensajes de depuración"))
    parser.add_argument("--seguro", action="store_true", help=_("Ejecuta en modo seguro"))
    parser.add_argument("--lang", default=os.environ.get("COBRA_LANG", "es"), help=_("Código de idioma para la interfaz"))
    parser.add_argument(
        "--validadores-extra",
        help="Ruta a módulo con validadores personalizados",
    )

    subparsers = parser.add_subparsers(dest="comando")

    comandos = [
        CompileCommand(),
        ExecuteCommand(),
        ModulesCommand(),
        DependenciasCommand(),
        DocsCommand(),
        EmpaquetarCommand(),
        CrearCommand(),
        InitCommand(),
        AgixCommand(),
        JupyterCommand(),
        FletCommand(),
        PluginsCommand(),
        InteractiveCommand(),
    ]
    comandos.extend(descubrir_plugins())

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
    setup_gettext(args.lang)
    command = getattr(args, "cmd", command_map["interactive"])
    resultado = command.run(args)
    return 0 if resultado is None else resultado


if __name__ == "__main__":
    sys.exit(main())
