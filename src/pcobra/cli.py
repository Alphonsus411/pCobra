import argparse
import contextlib
import io
import logging
import sys
from typing import List, Optional

from . import cobra as cobra_pkg
from . import core as core_pkg
from . import compiler as compiler_pkg

# Registrar alias de paquetes para compatibilidad con imports absolutos
sys.modules.setdefault("cobra", cobra_pkg)
sys.modules.setdefault("core", core_pkg)
sys.modules.setdefault("compiler", compiler_pkg)

import re

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - rama dependiente del entorno
    load_dotenv = None
from .cobra.cli.commands.compile_cmd import CompileCommand, LANG_CHOICES
from .cobra.cli.commands.execute_cmd import ExecuteCommand
from .cobra.cli.utils import messages

logger = logging.getLogger(__name__)


def configurar_entorno() -> None:
    """Carga variables de entorno desde un archivo .env si está presente."""
    if load_dotenv is None:
        logger.debug(
            "python-dotenv no está instalado; se omite la carga automática del archivo .env"
        )
        return
    try:
        cargado = load_dotenv()
    except OSError as exc:
        logger.error("No se pudo acceder al archivo .env: %s", exc)
        return
    except Exception as exc:  # pragma: no cover - registro y propagación
        logger.exception("Error inesperado al cargar variables de entorno")
        raise
    if not cargado:
        logger.warning("El archivo .env no se cargó")


cobra = argparse.ArgumentParser(prog="cobra")
subparsers = cobra.add_subparsers(dest="comando")

ejecutar_parser = subparsers.add_parser(
    "ejecutar", help="Ejecuta un programa Cobra"
)
ejecutar_parser.add_argument(
    "archivo", help="Ruta al archivo a ejecutar"
)
ejecutar_parser.add_argument(
    "--sandbox", action="store_true", help="Ejecuta el código en una sandbox"
)
ejecutar_parser.add_argument(
    "--contenedor",
    choices=["python", "js", "cpp", "rust"],
    help="Ejecuta el código en un contenedor Docker",
)

transpilar_parser = subparsers.add_parser(
    "transpilar", help="Transpila código Cobra"
)
transpilar_parser.add_argument(
    "archivo", help="Ruta al archivo a transpilar"
)
transpilar_parser.add_argument(
    "--a", "--lenguaje",
    dest="lenguaje",
    choices=LANG_CHOICES,
    default="python",
    help="Lenguaje de salida",
)
transpilar_parser.add_argument(
    "--backend",
    dest="backend",
    choices=LANG_CHOICES,
    default=None,
    help="Alias de --lenguaje para integraciones",
)
transpilar_parser.add_argument(
    "--o", "--salida",
    dest="salida",
    help="Archivo donde guardar el código generado",
)

def mostrar_ayuda(_: argparse.Namespace) -> int:
    """Imprime la ayuda general del programa."""
    cobra.print_help()
    return 0


ayuda_parser = subparsers.add_parser("ayuda", help="Muestra esta ayuda y sale")
ayuda_parser.set_defaults(func=mostrar_ayuda)


def main(argumentos: Optional[List[str]] = None) -> int:
    """Punto de entrada principal para la ejecución del CLI."""
    configurar_entorno()
    args = cobra.parse_args(argumentos)
    if args.comando is None:
        cobra.print_help()
        return 0
    if args.comando == "ejecutar":
        comando = ExecuteCommand()
        try:
            return comando.run(args)
        except Exception as exc:  # pragma: no cover - captura errores imprevistos
            logger.error("Error al ejecutar: %s", exc)
            return 1
    if args.comando == "transpilar":
        comando = CompileCommand()
        compile_args = argparse.Namespace(
            archivo=args.archivo,
            tipo=args.lenguaje,
            backend=getattr(args, "backend", None),
            tipos=None,
        )
        if args.salida:
            messages.disable_colors()
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                resultado = comando.run(compile_args)
            output = buffer.getvalue()
            output = re.sub(r"\x1b\[[0-9;]*m", "", output)
            lineas = [l for l in output.splitlines() if not l.startswith("Código generado")]
            output = "\n".join(lineas)
            if output and not output.endswith("\n"):
                output += "\n"
            with open(args.salida, "w", encoding="utf-8") as f:
                f.write(output)
            return resultado
        return comando.run(compile_args)
    if args.comando == "ayuda":
        return args.func(args)
    cobra.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
