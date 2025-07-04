"""Utilidades para limitar memoria y tiempo de CPU."""
from __future__ import annotations


def limitar_memoria_mb(mb: int) -> None:
    """Restringe la memoria máxima del proceso actual."""
    bytes_ = mb * 1024 * 1024
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (bytes_, bytes_))
    except Exception:
        try:
            import psutil  # type: ignore
            psutil.Process().rlimit(psutil.RLIMIT_AS, (bytes_, bytes_))
        except Exception as exc:  # pragma: no cover - fallo improbable
            raise RuntimeError("No se pudo establecer el límite de memoria") from exc


def limitar_cpu_segundos(segundos: int) -> None:
    """Limita el tiempo de CPU en segundos para este proceso."""
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (segundos, segundos))
    except Exception:
        try:
            import psutil  # type: ignore
            psutil.Process().rlimit(psutil.RLIMIT_CPU, (segundos, segundos))
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("No se pudo establecer el límite de CPU") from exc
