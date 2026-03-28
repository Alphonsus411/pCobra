import logging
import sys
from importlib import import_module
from pathlib import Path
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

logger = logging.getLogger(__name__)


def _alias_module(origen: str, destino: str):
    """Registra ``destino`` como alias del módulo ``origen``."""

    modulo = import_module(origen)
    sys.modules.setdefault(destino, modulo)
    return modulo


def _configurar_alias_paquete_cli() -> None:
    """Expone ``pcobra.cobra.cli`` como si fuese ``pcobra.cli``."""

    paquete_cli = _alias_module("pcobra.cobra.cli", "pcobra.cli")
    if hasattr(paquete_cli, "__path__"):
        globals()["__path__"] = list(paquete_cli.__path__)  # type: ignore[assignment]

    _alias_module("pcobra.cobra.cli.cli", "pcobra.cli.cli")


_configurar_alias_paquete_cli()

# Alias explícitos para compatibilidad histórica con ``import cli``.
sys.modules.setdefault("cli", sys.modules["pcobra.cli"])
sys.modules.setdefault("cli.cli", sys.modules["pcobra.cli.cli"])

# Reexporte de conveniencia para código legado.
cli = sys.modules["pcobra.cli.cli"]


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
    except Exception:  # pragma: no cover - registro y propagación
        logger.exception("Error inesperado al cargar variables de entorno")
        raise
    if not cargado:
        logger.warning("El archivo .env no se cargó")


def _normalizar_argumentos(argumentos: Optional[Iterable[str]]) -> Optional[List[str]]:
    """Devuelve una copia de ``argumentos`` con alias habituales corregidos."""

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
    from .cobra.cli.cli import CliApplication

    configurar_entorno()
    aplicacion = CliApplication()
    argv_entrada: Iterable[str] = argumentos if argumentos is not None else sys.argv[1:]
    argv = _normalizar_argumentos(argv_entrada)
    return aplicacion.run(argv)


if __name__ == "__main__":
    sys.exit(main())
