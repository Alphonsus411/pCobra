import argparse
import logging
import os
import sys

from src.cli.commands.agix_cmd import AgixCommand
from src.cli.commands.bench_cmd import BenchCommand
from src.cli.commands.bench_transpilers_cmd import BenchTranspilersCommand
from src.cli.commands.benchmarks2_cmd import BenchmarksV2Command
from src.cli.commands.benchmarks_cmd import BenchmarksCommand
from src.cli.commands.benchthreads_cmd import BenchThreadsCommand
from src.cli.commands.cache_cmd import CacheCommand
from src.cli.commands.compile_cmd import CompileCommand
from src.cli.commands.container_cmd import ContainerCommand
from src.cli.commands.crear_cmd import CrearCommand
from src.cli.commands.dependencias_cmd import DependenciasCommand
from src.cli.commands.docs_cmd import DocsCommand
from src.cli.commands.empaquetar_cmd import EmpaquetarCommand
from src.cli.commands.execute_cmd import ExecuteCommand
from src.cli.commands.flet_cmd import FletCommand
from src.cli.commands.init_cmd import InitCommand
from src.cli.commands.interactive_cmd import InteractiveCommand
from src.cli.commands.jupyter_cmd import JupyterCommand
from src.cli.commands.modules_cmd import ModulesCommand
from src.cli.commands.package_cmd import PaqueteCommand
from src.cli.commands.plugins_cmd import PluginsCommand
from src.cli.commands.profile_cmd import ProfileCommand
from src.cli.commands.qualia_cmd import QualiaCommand
from src.cli.commands.transpilar_inverso_cmd import TranspilarInversoCommand
from src.cli.commands.verify_cmd import VerifyCommand
from src.cli.i18n import _, format_traceback, setup_gettext
from src.cli.plugin import descubrir_plugins
from src.cli.utils import messages

# La configuración de logging solo debe activarse cuando la CLI se ejecuta
# directamente para evitar modificar la configuración global al importar este
# módulo desde las pruebas u otros paquetes.


def main(argv=None):
    """Punto de entrada principal de la CLI."""
    setup_gettext()
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    parser = argparse.ArgumentParser(prog="cobra", description=_("CLI para Cobra"))
    parser.add_argument(
        "--formatear",
        action="store_true",
        help=_("Formatea el archivo antes de procesarlo"),
    )
    parser.add_argument(
        "--depurar", action="store_true", help=_("Muestra mensajes de depuración")
    )
    parser.add_argument(
        "--seguro", action="store_true", help=_("Ejecuta en modo seguro")
    )
    parser.add_argument(
        "--lang",
        default=os.environ.get("COBRA_LANG", "es"),
        help=_("Código de idioma para la interfaz"),
    )
    parser.add_argument(
        "--no-color", action="store_true", help=_("Desactiva colores en la salida")
    )
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
        PaqueteCommand(),
        CrearCommand(),
        InitCommand(),
        AgixCommand(),
        JupyterCommand(),
        FletCommand(),
        ContainerCommand(),
        BenchCommand(),
        BenchmarksCommand(),
        BenchmarksV2Command(),
        BenchTranspilersCommand(),
        BenchThreadsCommand(),
        ProfileCommand(),
        QualiaCommand(),
        CacheCommand(),
        TranspilarInversoCommand(),
        VerifyCommand(),
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
    messages.disable_colors(args.no_color)
    messages.mostrar_logo()
    command = getattr(args, "cmd", command_map["interactive"])
    try:
        resultado = command.run(args)
    except Exception as exc:  # pragma: no cover - trazas manejadas
        logging.exception("Unhandled exception")
        messages.mostrar_error("Ocurri\u00f3 un error inesperado")
        print(format_traceback(exc, args.lang))
        return 1
    return 0 if resultado is None else resultado


if __name__ == "__main__":
    sys.exit(main())
