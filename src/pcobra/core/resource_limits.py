"""Utilidades centralizadas para limitar memoria y tiempo de CPU.

Todos los comandos deben emplear estas funciones en lugar de
implementaciones manuales para gestionar los límites de recursos."""
from __future__ import annotations

import logging
import os
import sys
from pcobra.core.cli.i18n import _


logger = logging.getLogger(__name__)
IS_WINDOWS = os.name == "nt" or sys.platform.startswith("win")


def limitar_memoria_mb(mb: int) -> None:
    """Restringe la memoria máxima del proceso actual."""
    bytes_ = mb * 1024 * 1024
    if IS_WINDOWS:
        if not _limitar_memoria_psutil(bytes_):
            logger.error(
                _(
                    "No se pudo establecer el límite de memoria en Windows; "
                    "el ajuste se omitirá."
                ),
            )
        return
    try:
        import resource
    except ImportError as exc:
        # Falta 'resource', se intenta 'psutil'.
        logger.warning(
            _("El módulo 'resource' no está disponible; se intentará 'psutil'."),
            exc_info=exc,
        )
        _limitar_memoria_psutil(bytes_)
        return
    try:
        resource.setrlimit(resource.RLIMIT_AS, (bytes_, bytes_))
    except (OSError, ValueError) as exc:
        # Error de configuración en 'resource'.
        logger.warning(
            _(
                "No se pudo configurar el límite de memoria con 'resource'; "
                "se intentará 'psutil'."
            ),
            exc_info=exc,
        )
        _limitar_memoria_psutil(bytes_)


def _limitar_memoria_psutil(bytes_: int) -> bool:
    try:
        import psutil  # type: ignore
    except ImportError as exc:
        mensaje = _("El módulo 'psutil' no está disponible para limitar la memoria.")
        if IS_WINDOWS:
            logger.warning(mensaje, exc_info=exc)
            return False
        logger.error(mensaje, exc_info=exc)
        raise RuntimeError(
            _("No se pudo establecer el límite de memoria en esta plataforma")
        ) from exc
    proc = psutil.Process()
    if not hasattr(proc, "rlimit"):
        mensaje = _(
            "psutil.Process no soporta 'rlimit'; no se aplicará el límite de memoria."
        )
        if IS_WINDOWS:
            logger.warning(mensaje)
            return False
        logger.error(mensaje)
        raise RuntimeError(
            _("No se pudo establecer el límite de memoria en esta plataforma")
        )
    try:
        proc.rlimit(psutil.RLIMIT_AS, (bytes_, bytes_))
        return True
    except (OSError, ValueError) as exc:
        mensaje = _("Error configurando el límite de memoria con 'psutil'.")
        if IS_WINDOWS:
            logger.warning(mensaje, exc_info=exc)
            return False
        logger.error(mensaje, exc_info=exc)
        raise RuntimeError(
            _("No se pudo establecer el límite de memoria en esta plataforma")
        ) from exc


def limitar_cpu_segundos(segundos: int) -> None:
    """Limita el tiempo de CPU en segundos para este proceso."""
    if IS_WINDOWS:
        if not _limitar_cpu_psutil(segundos):
            logger.error(
                _(
                    "No se pudo establecer el límite de CPU en Windows; "
                    "el ajuste se omitirá."
                )
            )
        return
    try:
        import resource
    except ImportError as exc:
        # Falta 'resource', se intenta 'psutil'.
        logger.warning(
            _("El módulo 'resource' no está disponible; se intentará 'psutil'."),
            exc_info=exc,
        )
        _limitar_cpu_psutil(segundos)
        return
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (segundos, segundos))
    except (OSError, ValueError) as exc:
        # Error de configuración en 'resource'.
        logger.warning(
            _(
                "No se pudo configurar el límite de CPU con 'resource'; "
                "se intentará 'psutil'."
            ),
            exc_info=exc,
        )
        _limitar_cpu_psutil(segundos)


def _limitar_cpu_psutil(segundos: int) -> bool:
    try:
        import psutil  # type: ignore
    except ImportError as exc:
        mensaje = _("El módulo 'psutil' no está disponible para limitar la CPU.")
        if IS_WINDOWS:
            logger.warning(mensaje, exc_info=exc)
            return False
        logger.error(mensaje, exc_info=exc)
        raise RuntimeError(
            _("No se pudo establecer el límite de CPU en esta plataforma")
        ) from exc
    proc = psutil.Process()
    if not hasattr(proc, "rlimit"):
        mensaje = _(
            "psutil.Process no soporta 'rlimit'; no se aplicará el límite de CPU."
        )
        if IS_WINDOWS:
            logger.warning(mensaje)
            return False
        logger.error(mensaje)
        raise RuntimeError(
            _("No se pudo establecer el límite de CPU en esta plataforma")
        )
    try:
        proc.rlimit(psutil.RLIMIT_CPU, (segundos, segundos))
        return True
    except (OSError, ValueError) as exc:
        mensaje = _("Error configurando el límite de CPU con 'psutil'.")
        if IS_WINDOWS:
            logger.warning(mensaje, exc_info=exc)
            return False
        logger.error(mensaje, exc_info=exc)
        raise RuntimeError(
            _("No se pudo establecer el límite de CPU en esta plataforma")
        ) from exc
