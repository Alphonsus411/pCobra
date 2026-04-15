"""Modelos base para describir el contrato de stdlib."""

from dataclasses import dataclass
from typing import Literal


CoverageLevel = Literal["full", "partial"]


@dataclass(frozen=True)
class FunctionCoverage:
    """Cobertura de una función Cobra por backend."""

    function: str
    backend_levels: dict[str, CoverageLevel]


@dataclass(frozen=True)
class RuntimeMapping:
    """Mapeo del módulo contractual a implementaciones existentes."""

    standard_library: tuple[str, ...]
    corelibs: tuple[str, ...]
    core_nativos: tuple[str, ...]


@dataclass(frozen=True)
class ContractDescriptor:
    """Descriptor contractual completo por módulo."""

    module: str
    public_api: tuple[str, ...]
    primary_backend: str
    allowed_fallback: tuple[str, ...]
    runtime_mapping: RuntimeMapping
    coverage: tuple[FunctionCoverage, ...]
