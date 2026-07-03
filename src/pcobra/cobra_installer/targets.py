"""Tipos de destino soportados por el instalador Cobra."""

from __future__ import annotations

import platform
import warnings
from dataclasses import dataclass
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

    @classmethod
    def from_value(cls, value: "TargetOS | str") -> "TargetOS":
        """Normaliza aliases de usuario al sistema operativo canónico."""

        if isinstance(value, cls):
            return value
        normalized = str(value).strip().lower().replace("_", "-")
        if normalized == "current":
            return detect_host_os()
        aliases = {
            "win": cls.WINDOWS,
            "win32": cls.WINDOWS,
            "windows": cls.WINDOWS,
            "linux": cls.LINUX,
            "gnu-linux": cls.LINUX,
            "darwin": cls.MACOS,
            "mac": cls.MACOS,
            "macos": cls.MACOS,
            "mac-os": cls.MACOS,
            "osx": cls.MACOS,
            "os-x": cls.MACOS,
        }
        try:
            return aliases[normalized]
        except KeyError as exc:
            supported = ", ".join((*VALID_TARGET_VALUES, "current"))
            raise ValueError(
                f"Target no soportado: {value!r}. Valores válidos: {supported}."
            ) from exc

    @property
    def expected_artifact(self) -> "ExpectedArtifact":
        """Describe el artefacto final esperado para este sistema operativo."""

        return EXPECTED_ARTIFACTS[self]


class BuilderKind(StrEnum):
    """Tipos de builder soportados o reservados para aislar builds."""

    LOCAL = "local"
    DOCKER = "docker"
    VM = "vm"
    CI = "ci"
    REMOTE = "remote"

    @classmethod
    def from_value(cls, value: "BuilderKind | str | None") -> "BuilderKind":
        """Normaliza la selección de builder sin activar implementaciones futuras."""

        if value is None:
            return cls.LOCAL
        if isinstance(value, cls):
            return value
        return cls(str(value).strip().lower())


# Alias de compatibilidad: la API pública histórica exportaba ``Builder``.
Builder = BuilderKind


@dataclass(frozen=True, slots=True)
class BuilderConfig:
    """Esqueleto de configuración para builders futuros."""

    builder: BuilderKind = BuilderKind.LOCAL
    image: str | None = None
    vm_name: str | None = None
    ci_runner: str | None = None
    remote_url: str | None = None

    @classmethod
    def from_value(
        cls, value: "BuilderConfig | BuilderKind | str | None"
    ) -> "BuilderConfig":
        """Crea una configuración mínima desde un builder o cadena."""

        if isinstance(value, cls):
            return value
        return cls(builder=BuilderKind.from_value(value))


@dataclass(frozen=True, slots=True)
class ExpectedArtifact:
    """Formato final esperado para el artefacto de PyInstaller."""

    description: str
    extension: str | None = None
    bundle_extension: str | None = None


VALID_TARGET_VALUES = tuple(target.value for target in TargetOS)
EXPECTED_ARTIFACTS: dict[TargetOS, ExpectedArtifact] = {
    TargetOS.WINDOWS: ExpectedArtifact(
        description="ejecutable Windows", extension=".exe"
    ),
    TargetOS.LINUX: ExpectedArtifact(description="binario ELF", extension=None),
    TargetOS.MACOS: ExpectedArtifact(
        description="bundle .app o binario macOS", bundle_extension=".app"
    ),
}
CROSS_COMPILATION_WARNING = (
    "El target seleccionado ({target}) no coincide con el host actual ({host}). "
    "PyInstaller no soporta cross-compilation de forma nativa. Para generar "
    "artefactos de otro sistema operativo, usa Docker, una Máquina Virtual, "
    "un runner CI/CD o un builder remoto."
)


def detect_host_os() -> TargetOS:
    """Detecta el sistema operativo host y lo normaliza a TargetOS."""

    system = platform.system().strip().lower()
    if system == "windows":
        return TargetOS.WINDOWS
    if system == "linux":
        return TargetOS.LINUX
    if system == "darwin":
        return TargetOS.MACOS
    raise RuntimeError(f"Host no soportado para build Cobra: {platform.system()!r}.")


def normalize_target(value: TargetOS | str) -> TargetOS:
    """Normaliza targets admitiendo ``current`` como alias del host actual."""

    return TargetOS.from_value(value)


def validate_target(value: TargetOS | str, *, warn_on_cross: bool = True) -> TargetOS:
    """Valida el target y advierte cuando no coincide con el host actual."""

    target = normalize_target(value)
    host = detect_host_os()
    if warn_on_cross and target is not host:
        warnings.warn(
            CROSS_COMPILATION_WARNING.format(target=target.value, host=host.value),
            RuntimeWarning,
            stacklevel=2,
        )
    return target


def expected_artifact_for(target: TargetOS | str) -> ExpectedArtifact:
    """Devuelve la extensión o formato final esperado para un target."""

    return normalize_target(target).expected_artifact


__all__ = [
    "BuildMode",
    "Builder",
    "BuilderKind",
    "BuilderConfig",
    "CROSS_COMPILATION_WARNING",
    "EXPECTED_ARTIFACTS",
    "ExpectedArtifact",
    "TargetOS",
    "VALID_TARGET_VALUES",
    "detect_host_os",
    "expected_artifact_for",
    "normalize_target",
    "validate_target",
]
