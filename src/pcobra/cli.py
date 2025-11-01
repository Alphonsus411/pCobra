import importlib
import logging
import sys
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Iterable, List, Optional

if __package__ in {None, ""}:
    # Permite ejecutar ``python src/pcobra/cli.py`` sin errores de importación.
    paquete_raiz = Path(__file__).resolve().parent.parent
    ruta_paquete = str(paquete_raiz)
    if ruta_paquete not in sys.path:
        sys.path.insert(0, ruta_paquete)
    __package__ = "pcobra"

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - rama dependiente del entorno
    load_dotenv = None

from pcobra import cobra as cobra_pkg
from pcobra import compiler as compiler_pkg
from pcobra import core as core_pkg
from pcobra.cobra.cli import commands as cobra_cli_commands

logger = logging.getLogger(__name__)


def _alias_module(origen: str, destino: str) -> ModuleType:
    """Registra ``destino`` como alias del módulo ``origen``."""

    modulo = import_module(origen)
    sys.modules.setdefault(destino, modulo)
    return modulo


# Alias explícitos hacia el paquete real de comandos del CLI
cli = _alias_module("pcobra.cobra.cli.cli", "pcobra.cli.cli")
commands = cobra_cli_commands


def _configurar_alias_paquete_cli() -> None:
    """Expone ``pcobra.cobra.cli`` como si fuese ``pcobra.cli``.

    El proyecto mantiene compatibilidad histórica con importaciones que
    asumían que ``pcobra.cli`` era un paquete. Sin embargo, el fichero
    actual se llama ``cli.py`` y, por tanto, Python lo trata como un
    módulo en lugar de paquete, lo que rompe importaciones como
    ``pcobra.cli.utils``. Para evitar ``ModuleNotFoundError`` registramos
    alias explícitos y propagamos el ``__path__`` del paquete real.
    """

    paquete_cli = _alias_module("pcobra.cobra.cli", "pcobra.cli")
    # Marcar el módulo como paquete reexportando su ``__path__`` original.
    if hasattr(paquete_cli, "__path__"):
        globals()["__path__"] = list(paquete_cli.__path__)  # type: ignore[assignment]

    _alias_module("pcobra.cobra.cli.commands", "pcobra.cli.commands")
    _alias_module("pcobra.cobra.cli.utils", "pcobra.cli.utils")
    _alias_module("pcobra.cobra.cli.utils.semver", "pcobra.cli.utils.semver")


_configurar_alias_paquete_cli()
from pcobra.cobra.cli.cli import CliApplication

# Registrar alias de paquetes para compatibilidad con imports absolutos
sys.modules.setdefault("cobra", cobra_pkg)
sys.modules.setdefault("core", core_pkg)
sys.modules.setdefault("compiler", compiler_pkg)


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


def _normalizar_argumentos(argumentos: Optional[Iterable[str]]) -> Optional[List[str]]:
    """Devuelve una copia de ``argumentos`` con alias habituales corregidos.

    Los usuarios de la antigua CLI podían invocar ``python -m pcobra.cli ayuda``
    para mostrar la ayuda general. Tras la reestructuración del paquete,
    ``ayuda`` dejó de ser una orden válida y provocaba ``invalid choice``. Aquí
    interceptamos esos casos para redirigirlos hacia las banderas oficiales del
    analizador de argumentos.
    """

    if argumentos is None:
        return None

    normalizados = list(argumentos)
    if not normalizados:
        return normalizados

    primer_argumento = normalizados[0].lower()
    if primer_argumento in {"ayuda", "help"}:
        normalizados[0:1] = ["--ayuda"]

    return normalizados


def main(argumentos: Optional[List[str]] = None) -> int:
    """Punto de entrada principal para la ejecución del CLI."""
    configurar_entorno()
    aplicacion = CliApplication()
    argv_entrada: Iterable[str] = argumentos if argumentos is not None else sys.argv[1:]
    argv = _normalizar_argumentos(argv_entrada)
    return aplicacion.run(argv)


if __name__ == "__main__":
    sys.exit(main())
