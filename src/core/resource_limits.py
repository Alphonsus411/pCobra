"""Utilidades centralizadas para limitar memoria y tiempo de CPU.

Todos los comandos deben emplear estas funciones en lugar de
implementaciones manuales para gestionar los límites de recursos."""
from __future__ import annotations

import logging


logger = logging.getLogger(__name__)


def limitar_memoria_mb(mb: int) -> None:
    """Restringe la memoria máxima del proceso actual."""
    bytes_ = mb * 1024 * 1024
    try:
        import resource
    except ImportError as exc:
        # Falta 'resource', se intenta 'psutil'.
        logger.warning(
            "El módulo 'resource' no está disponible; se intentará 'psutil'.",
            exc_info=exc,
        )
        _limitar_memoria_psutil(bytes_)
        return
    try:
        resource.setrlimit(resource.RLIMIT_AS, (bytes_, bytes_))
    except (OSError, ValueError) as exc:
        # Error de configuración en 'resource'.
        logger.warning(
            "No se pudo configurar el límite de memoria con 'resource'; se intentará 'psutil'.",
            exc_info=exc,
        )
        _limitar_memoria_psutil(bytes_)


def _limitar_memoria_psutil(bytes_: int) -> None:
    try:
        import psutil  # type: ignore
    except ImportError as exc:
        # Falta 'psutil'; no hay forma de establecer el límite.
        logger.error(
            "El módulo 'psutil' no está disponible para limitar la memoria.",
            exc_info=exc,
        )
        raise RuntimeError("No se pudo establecer el límite de memoria") from exc
    try:
        psutil.Process().rlimit(psutil.RLIMIT_AS, (bytes_, bytes_))
    except (OSError, ValueError) as exc:
        # Error de configuración en 'psutil'.
        logger.error(
            "Error configurando el límite de memoria con 'psutil'.",
            exc_info=exc,
        )
        raise RuntimeError("No se pudo establecer el límite de memoria") from exc


def limitar_cpu_segundos(segundos: int) -> None:
    """Limita el tiempo de CPU en segundos para este proceso."""
    try:
        import resource
    except ImportError as exc:
        # Falta 'resource', se intenta 'psutil'.
        logger.warning(
            "El módulo 'resource' no está disponible; se intentará 'psutil'.",
            exc_info=exc,
        )
        _limitar_cpu_psutil(segundos)
        return
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (segundos, segundos))
    except (OSError, ValueError) as exc:
        # Error de configuración en 'resource'.
        logger.warning(
            "No se pudo configurar el límite de CPU con 'resource'; se intentará 'psutil'.",
            exc_info=exc,
        )
        _limitar_cpu_psutil(segundos)


def _limitar_cpu_psutil(segundos: int) -> None:
    try:
        import psutil  # type: ignore
    except ImportError as exc:
        # Falta 'psutil'; no hay forma de establecer el límite.
        logger.error(
            "El módulo 'psutil' no está disponible para limitar la CPU.",
            exc_info=exc,
        )
        raise RuntimeError("No se pudo establecer el límite de CPU") from exc
    try:
        psutil.Process().rlimit(psutil.RLIMIT_CPU, (segundos, segundos))
    except (OSError, ValueError) as exc:
        # Error de configuración en 'psutil'.
        logger.error(
            "Error configurando el límite de CPU con 'psutil'.",
            exc_info=exc,
        )
        raise RuntimeError("No se pudo establecer el límite de CPU") from exc
