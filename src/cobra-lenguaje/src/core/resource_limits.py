"""Envoltorio que reexporta las utilidades de ``core.resource_limits``."""
from __future__ import annotations

from core.resource_limits import limitar_memoria_mb, limitar_cpu_segundos

__all__ = ["limitar_memoria_mb", "limitar_cpu_segundos"]
