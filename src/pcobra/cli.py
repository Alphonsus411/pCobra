import importlib
import logging
import sys
from typing import List, Optional

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - rama dependiente del entorno
    load_dotenv = None

from . import cobra as cobra_pkg
from . import compiler as compiler_pkg
from . import core as core_pkg
from .cobra.cli import commands as cobra_cli_commands

# Alias explícitos hacia el paquete real de comandos del CLI
cli = importlib.import_module("pcobra.cobra.cli.cli")
commands = cobra_cli_commands
sys.modules.setdefault("pcobra.cli.cli", cli)
sys.modules.setdefault("pcobra.cli.commands", cobra_cli_commands)
from .cobra.cli.cli import CliApplication

# Registrar alias de paquetes para compatibilidad con imports absolutos
sys.modules.setdefault("cobra", cobra_pkg)
sys.modules.setdefault("core", core_pkg)
sys.modules.setdefault("compiler", compiler_pkg)

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


def main(argumentos: Optional[List[str]] = None) -> int:
    """Punto de entrada principal para la ejecución del CLI."""
    configurar_entorno()
    aplicacion = CliApplication()
    return aplicacion.run(argumentos)


if __name__ == "__main__":
    sys.exit(main())
