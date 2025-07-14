"""Estructuras de la tabla de símbolos y manejo jerárquico de ámbitos."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Simbolo:
    nombre: str
    tipo: str  # 'variable', 'funcion', 'clase'


class Ambito:
    def __init__(self, padre: Optional['Ambito'] = None):
        self.padre = padre
        self.simbolos: Dict[str, Simbolo] = {}

    def declarar(self, nombre: str, tipo: str):
        if nombre in self.simbolos:
            raise ValueError(f"Simbolo ya declarado en este ámbito: {nombre}")
        self.simbolos[nombre] = Simbolo(nombre, tipo)

    def resolver(self, nombre: str) -> Optional[Simbolo]:
        if nombre in self.simbolos:
            return self.simbolos[nombre]
        if self.padre:
            return self.padre.resolver(nombre)
        return None

    def resolver_local(self, nombre: str) -> Optional[Simbolo]:
        return self.simbolos.get(nombre)
