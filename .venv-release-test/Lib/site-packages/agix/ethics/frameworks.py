from __future__ import annotations

"""Marcos éticos básicos con configuraciones simples."""

from typing import Dict, Sequence


def _clasificar_basico(score: float) -> str:
    if score > 0.85:
        return "justo"
    if score > 0.6:
        return "aceptable"
    if score > 0.4:
        return "cuestionable"
    return "nocivo"


class UtilitarianEthics:
    """Evalúa acciones según una suma ponderada de consecuencias."""

    def __init__(self, pesos: Dict[str, float] | None = None):
        self.pesos = pesos or {}

    def evaluar(self, accion: Dict[str, float]) -> float:
        total_peso = 0.0
        total = 0.0
        for k, v in accion.items():
            peso = self.pesos.get(k, 1.0)
            total += peso * v
            total_peso += peso
        return total / total_peso if total_peso else 0.0

    def clasificar(self, score: float) -> str:
        return _clasificar_basico(score)


class DeontologicalEthics:
    """Evalúa según el cumplimiento de reglas predefinidas."""

    def __init__(self, reglas: Dict[str, float] | None = None):
        self.reglas = reglas or {}

    def evaluar(self, accion: Dict[str, float]) -> float:
        if not self.reglas:
            return 0.0
        cumplidas = sum(
            1 for k, minimo in self.reglas.items() if accion.get(k, 0.0) >= minimo
        )
        return cumplidas / len(self.reglas)

    def clasificar(self, score: float) -> str:
        return _clasificar_basico(score)


class VirtueEthics:
    """Evalúa acciones según virtudes priorizadas."""

    def __init__(self, virtudes: Sequence[str] | None = None):
        self.virtudes = list(virtudes or [])

    def evaluar(self, accion: Dict[str, float]) -> float:
        if not self.virtudes:
            return sum(accion.values()) / len(accion) if accion else 0.0
        return sum(accion.get(v, 0.0) for v in self.virtudes) / len(self.virtudes)

    def clasificar(self, score: float) -> str:
        return _clasificar_basico(score)
