"""Estructuras JSON/CPU para fractales holográficos de Holobit.

Este módulo es deliberadamente independiente de la API pública histórica de
``crear_holobit``.  No añade campos a los payloads ``{"tipo": "holobit",
"valores": [...]}`` y utiliza un tipo propio para serialización fractal:
``{"tipo": "holographic_fractal", ...}``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, TypeAlias

HOLOGRAPHIC_DIMENSIONS = 10

JSONPrimitive: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONPrimitive | list["JSONValue"] | dict[str, "JSONValue"]
SymbolicExpression: TypeAlias = dict[str, JSONValue]


def _es_numero_dimensional(valor: Any) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_json_estable(valor: Any) -> None:
    if valor is None or isinstance(valor, (str, int, float, bool)):
        return
    if isinstance(valor, list):
        for item in valor:
            _validar_json_estable(item)
        return
    if isinstance(valor, dict):
        for clave, contenido in valor.items():
            if not isinstance(clave, str):
                raise TypeError("Las claves JSON del fractal holográfico deben ser texto")
            _validar_json_estable(contenido)
        return
    raise TypeError("El fractal holográfico solo acepta estructuras JSON estables")


def normalizar_vector_dimensional(vector: Sequence[Any]) -> list[float]:
    """Normaliza un vector cuantificable a ``list[float]`` de longitud 10."""

    if isinstance(vector, (str, bytes)):
        raise TypeError("El vector dimensional debe ser una secuencia numérica")
    if len(vector) != HOLOGRAPHIC_DIMENSIONS:
        raise ValueError(
            "El vector dimensional debe contener "
            f"exactamente {HOLOGRAPHIC_DIMENSIONS} dimensiones"
        )
    salida: list[float] = []
    for valor in vector:
        if not _es_numero_dimensional(valor):
            raise TypeError("Cada dimensión cuantificable debe ser numérica")
        salida.append(float(valor))
    return salida


def normalizar_expresion_simbolica(expresion: Mapping[str, Any]) -> SymbolicExpression:
    """Valida una expresión simbólica JSON estable sin evaluar código externo."""

    if not isinstance(expresion, Mapping):
        raise TypeError("La expresión simbólica debe ser un objeto JSON")
    salida: SymbolicExpression = dict(expresion)
    if salida.get("symbolic") is not True:
        raise ValueError("La expresión simbólica debe declarar symbolic=true")
    if not isinstance(salida.get("expression"), str):
        raise TypeError("La expresión simbólica debe incluir expression como texto")
    _validar_json_estable(salida)
    return salida


@dataclass(frozen=True)
class Holocron:
    """Metadatos JSON estables asociados a un fractal holográfico."""

    id: str
    metadata: dict[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise TypeError("El id del holocron debe ser texto no vacío")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata debe ser un objeto JSON")
        _validar_json_estable(self.metadata)

    def to_json(self) -> dict[str, JSONValue]:
        return {"id": self.id, "metadata": dict(self.metadata)}

    @classmethod
    def from_json(cls, payload: Mapping[str, Any]) -> Holocron:
        if not isinstance(payload, Mapping):
            raise TypeError("El holocron debe ser un objeto JSON")
        id_holocron = payload["id"]
        if not isinstance(id_holocron, str):
            raise TypeError("El id del holocron debe ser texto")
        return cls(id=id_holocron, metadata=dict(payload.get("metadata", {})))


@dataclass(frozen=True)
class DimensionalDensity:
    """Densidad dimensional cuantificable o simbólica en diez dimensiones."""

    vector: list[float] | None = None
    symbolic: SymbolicExpression | None = None

    def __post_init__(self) -> None:
        if (self.vector is None) == (self.symbolic is None):
            raise ValueError("La densidad debe ser cuantificable o simbólica, no ambas")
        if self.vector is not None:
            object.__setattr__(
                self,
                "vector",
                normalizar_vector_dimensional(self.vector),
            )
        if self.symbolic is not None:
            object.__setattr__(
                self,
                "symbolic",
                normalizar_expresion_simbolica(self.symbolic),
            )

    @classmethod
    def from_vector(cls, vector: Sequence[Any]) -> DimensionalDensity:
        return cls(vector=normalizar_vector_dimensional(vector))

    @classmethod
    def from_symbolic(cls, expression: str) -> DimensionalDensity:
        if not isinstance(expression, str) or not expression:
            raise TypeError("La expresión simbólica debe ser texto no vacío")
        return cls(symbolic={"symbolic": True, "expression": expression})

    def to_json(self) -> dict[str, JSONValue]:
        if self.symbolic is not None:
            return dict(self.symbolic)
        if self.vector is None:  # pragma: no cover - protegido por __post_init__
            raise ValueError("Densidad dimensional inválida")
        return {"symbolic": False, "vector": list(self.vector)}

    @classmethod
    def from_json(cls, payload: Sequence[Any] | Mapping[str, Any]) -> DimensionalDensity:
        if isinstance(payload, Mapping) and payload.get("symbolic") is True:
            return cls(symbolic=normalizar_expresion_simbolica(payload))
        if isinstance(payload, Mapping) and payload.get("symbolic") is False:
            vector = payload.get("vector")
            if not isinstance(vector, Sequence):
                raise TypeError("La densidad cuantificable debe incluir un vector")
            return cls.from_vector(vector)
        if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
            return cls.from_vector(payload)
        raise TypeError("La densidad dimensional debe ser vector o expresión simbólica")


@dataclass(frozen=True)
class FractalNode:
    """Nodo puramente serializable de un fractal holográfico."""

    id: str
    density: DimensionalDensity
    children: tuple[FractalNode, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise TypeError("El id del nodo fractal debe ser texto no vacío")
        if not isinstance(self.density, DimensionalDensity):
            raise TypeError("density debe ser una instancia de DimensionalDensity")
        hijos = tuple(self.children)
        for child in hijos:
            if not isinstance(child, FractalNode):
                raise TypeError("children solo puede contener nodos fractales")
        object.__setattr__(self, "children", hijos)

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "id": self.id,
            "density": self.density.to_json(),
            "children": [child.to_json() for child in self.children],
        }

    @classmethod
    def from_json(cls, payload: Mapping[str, Any]) -> FractalNode:
        if not isinstance(payload, Mapping):
            raise TypeError("El nodo fractal debe ser un objeto JSON")
        id_nodo = payload["id"]
        if not isinstance(id_nodo, str):
            raise TypeError("El id del nodo fractal debe ser texto")
        return cls(
            id=id_nodo,
            density=DimensionalDensity.from_json(payload["density"]),
            children=tuple(cls.from_json(child) for child in payload.get("children", [])),
        )


@dataclass(frozen=True)
class HolographicFractal:
    """Fractal holográfico con serialización separada de ``holobit``."""

    holocron: Holocron
    root: FractalNode

    def __post_init__(self) -> None:
        if not isinstance(self.holocron, Holocron):
            raise TypeError("holocron debe ser una instancia de Holocron")
        if not isinstance(self.root, FractalNode):
            raise TypeError("root debe ser una instancia de FractalNode")

    def to_json(self) -> dict[str, JSONValue]:
        payload: dict[str, JSONValue] = {
            "tipo": "holographic_fractal",
            "holocron": self.holocron.to_json(),
            "root": self.root.to_json(),
        }
        _validar_json_estable(payload)
        return payload

    @classmethod
    def from_json(cls, payload: Mapping[str, Any]) -> HolographicFractal:
        if not isinstance(payload, Mapping):
            raise TypeError("El fractal holográfico debe ser un objeto JSON")
        if payload.get("tipo") != "holographic_fractal":
            raise ValueError("El tipo debe ser holographic_fractal")
        return cls(
            holocron=Holocron.from_json(payload["holocron"]),
            root=FractalNode.from_json(payload["root"]),
        )


__all__ = [
    "HOLOGRAPHIC_DIMENSIONS",
    "Holocron",
    "FractalNode",
    "DimensionalDensity",
    "HolographicFractal",
    "normalizar_vector_dimensional",
    "normalizar_expresion_simbolica",
]
