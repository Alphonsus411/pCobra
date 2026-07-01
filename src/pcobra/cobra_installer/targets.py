"""Tipos de destino soportados por el instalador Cobra."""

from __future__ import annotations

from enum import StrEnum


class BuildMode(StrEnum):
    """Modos de empaquetado compatibles con PyInstaller."""

    ONEFILE = "onefile"
    ONEDIR = "onedir"

    @classmethod
    def from_value(cls, value: "BuildMode | str") -> "BuildMode":
        """Normaliza cadenas o instancias de enum al modo de build canónico."""

        if isinstance(value, cls):
            return value
        return cls(str(value))


class TargetOS(StrEnum):
    """Sistemas operativos objetivo para un build Cobra."""

    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"


__all__ = ["BuildMode", "TargetOS"]
