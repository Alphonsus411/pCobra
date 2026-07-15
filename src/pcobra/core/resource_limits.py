"""Utilidades centralizadas para limitar memoria y tiempo de CPU.

Todos los comandos deben emplear estas funciones en lugar de
implementaciones manuales para gestionar los límites de recursos."""
from __future__ import annotations

import importlib
import logging
import os
import sys
from pcobra.core.cli.i18n import _


logger = logging.getLogger(__name__)
IS_WINDOWS = os.name == "nt" or sys.platform.startswith("win")

PSUTIL_FALLBACK_ENV = "PCOBRA_ALLOW_PSUTIL_FALLBACK"

# Evita emitir el mismo log de omisión en cada invocación (REPL/bucles).
_WINDOWS_SKIP_LOGGED = False


def _log_windows_skip_once() -> None:
    global _WINDOWS_SKIP_LOGGED
    if _WINDOWS_SKIP_LOGGED:
        return
    logger.info(_("Los límites de recursos no son compatibles con Windows; se omiten."))
    _WINDOWS_SKIP_LOGGED = True


def _cargar_psutil():
    """Carga ``psutil`` de forma controlada para minimizar superficie de ataque."""

    modulo = sys.modules.get("psutil")
    if modulo is not None:
        return modulo

    # Por seguridad, evitamos importar dinámicamente psutil salvo opt-in explícito.
    if os.environ.get(PSUTIL_FALLBACK_ENV) != "1":
        raise ImportError("dynamic psutil import disabled")

    return importlib.import_module("psutil")


def _validar_entero_positivo(nombre: str, valor: int | None) -> None:
    if valor is not None and valor <= 0:
        raise ValueError(f"{nombre} debe ser un entero positivo")


def _validar_limites_recursos(
    *, memoria_mb: int | None = None, cpu_segundos: int | None = None
) -> None:
    """Valida límites sin modificar recursos del proceso actual."""
    _validar_entero_positivo("memoria_mb", memoria_mb)
    _validar_entero_positivo("cpu_segundos", cpu_segundos)


def _aplicar_limites_proceso_hijo(
    *, memoria_mb: int | None = None, cpu_segundos: int | None = None
) -> None:
    """Aplica límites de recursos únicamente en un proceso hijo descartable.

    Esta función debe llamarse desde ``preexec_fn`` o desde el entrypoint de un
    worker ya aislado. No debe invocarse desde CLI, REPL, IDLE ni desde el
    proceso anfitrión del runner de pruebas.
    """
    _validar_limites_recursos(memoria_mb=memoria_mb, cpu_segundos=cpu_segundos)

    if memoria_mb is None and cpu_segundos is None:
        return
    if IS_WINDOWS:
        raise NotImplementedError(
            "Los límites de recursos no están soportados en Windows"
        )

    import resource

    if memoria_mb is not None:
        limite = memoria_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limite, limite))
    if cpu_segundos is not None:
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_segundos, cpu_segundos))


def limitar_memoria_mb(mb: int) -> None:
    """Valida el límite de memoria sin modificar el proceso anfitrión.

    Los límites efectivos de ejecución Cobra se aplican exclusivamente dentro
    de procesos hijos descartables. Esta función se conserva por compatibilidad
    con integraciones existentes, pero no llama a ``setrlimit`` sobre el
    proceso actual para evitar contaminar CLI, REPL, IDLE o el runner de tests.
    """
    _validar_entero_positivo("mb", mb)
    if IS_WINDOWS:  # psutil.Process.rlimit no está soportado en Windows.
        _log_windows_skip_once()


def _limitar_memoria_psutil(bytes_: int) -> bool:
    try:
        psutil = _cargar_psutil()  # type: ignore
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
    """Valida el límite de CPU sin modificar el proceso anfitrión.

    Los límites efectivos de ejecución Cobra se aplican exclusivamente dentro
    de procesos hijos descartables. Esta función se conserva por compatibilidad
    con integraciones existentes, pero no llama a ``setrlimit`` sobre el
    proceso actual para evitar contaminar CLI, REPL, IDLE o el runner de tests.
    """
    _validar_entero_positivo("segundos", segundos)
    if IS_WINDOWS:  # psutil.Process.rlimit no está soportado en Windows.
        _log_windows_skip_once()


def _limitar_cpu_psutil(segundos: int) -> bool:
    try:
        psutil = _cargar_psutil()  # type: ignore
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
