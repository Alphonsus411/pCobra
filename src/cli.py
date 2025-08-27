import argparse
import logging
import sys
from typing import List, Optional

from dotenv import load_dotenv
from cobra.cli.cli import main as cobra_cli_main

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
subparsers.add_parser("ejecutar", help="Ejecuta un programa Cobra")
subparsers.add_parser("transpilar", help="Transpila código Cobra")
subparsers.add_parser("ayuda", help="Muestra esta ayuda y sale")


def main(argumentos: Optional[List[str]] = None) -> int:
    """Punto de entrada principal para la ejecución del CLI."""
    configurar_entorno()
    args, extra = cobra.parse_known_args(argumentos)
    if args.comando == "ayuda" or args.comando is None:
        cobra.print_help()
        return 0
    if args.comando == "ejecutar":
        return cobra_cli_main(["execute", *extra])
    if args.comando == "transpilar":
        return cobra_cli_main(["compile", *extra])
    cobra.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
