import argparse
import contextlib
import io
import logging
import sys
from typing import List, Optional

from dotenv import load_dotenv
from .cobra.cli.commands.compile_cmd import CompileCommand, LANG_CHOICES
from .cobra.cli.commands.execute_cmd import ExecuteCommand

logger = logging.getLogger(__name__)


def configurar_entorno() -> None:
    """Carga variables de entorno desde un archivo .env si está presente."""
    try:
        if not load_dotenv():
            logger.warning("El archivo .env no se cargó")
    except Exception as exc:  # pragma: no cover - manejo básico de errores
        logger.critical(
            "Error inesperado al cargar variables de entorno: %s", str(exc)
        )
        raise


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
            archivo=args.archivo, tipo=args.lenguaje, backend=None, tipos=None
        )
        if args.salida:
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                resultado = comando.run(compile_args)
            with open(args.salida, "w", encoding="utf-8") as f:
                f.write(buffer.getvalue())
            return resultado
        return comando.run(compile_args)
    if args.comando == "ayuda":
        return args.func(args)
    cobra.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
