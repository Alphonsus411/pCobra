"""Modelos base para describir el contrato de stdlib."""

from dataclasses import dataclass


CoverageLevel = str  # full | partial


@dataclass(frozen=True)
class FunctionCoverage:
    """Cobertura de una función Cobra por backend."""

    function: str
    backend_levels: dict[str, CoverageLevel]


@dataclass(frozen=True)
class RuntimeMapping:
    """Mapeo del módulo contractual a implementaciones existentes."""

    standard_library: str | None
    corelibs: str | None
    core_nativos: str | None


@dataclass(frozen=True)
class ContractDescriptor:
    """Descriptor contractual completo por módulo."""

    module: str
    public_api: tuple[str, ...]
    primary_backend: str
    allowed_fallback: tuple[str, ...]
    runtime_mapping: RuntimeMapping
    coverage: tuple[FunctionCoverage, ...]
