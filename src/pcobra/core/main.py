"""Punto de entrada mínimo para ejecutar un saludo de prueba."""

from __future__ import annotations

import logging

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - dependencia opcional
    load_dotenv = None

logger = logging.getLogger(__name__)


def _cargar_dotenv() -> None:
    """Carga variables de entorno si :mod:`python-dotenv` está instalado."""

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
    except Exception:  # pragma: no cover - registro defensivo
        logger.exception("Error inesperado al cargar el archivo .env")
        raise
    if not cargado:
        logger.info("No se encontró archivo .env en el directorio actual")


def main():
    """Imprime un mensaje de bienvenida."""
    _cargar_dotenv()
    print("¡Hola desde Cobra!")


if __name__ == '__main__':
    main()
