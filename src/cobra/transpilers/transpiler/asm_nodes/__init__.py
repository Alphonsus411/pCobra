"""
Módulo de transpilación de código.
Implementa el patrón Visitor para procesar diferentes nodos del AST.
"""

import os
from typing import Any, Optional, List, Dict


class TranspiladorBase:
    """Clase base para la implementación de transpiladores."""

    def __init__(self):
        self.indent: int = 0
        self._output: List[str] = []

    def agregar_linea(self, linea: str) -> None:
        """
        Agrega una línea al output con la indentación actual.

        Args:
            linea: Texto a agregar
        """
        self._output.append("    " * self.indent + linea)

    def obtener_valor(self, nodo: Any) -> str:
        """
        Obtiene el valor representativo de un nodo.

        Args:
            nodo: Nodo del AST a procesar

        Returns:
            str: Representación en string del valor del nodo

        Raises:
            ValueError: Si el nodo no es válido o no se puede procesar
        """
        if nodo is None:
            raise ValueError("No se puede procesar un nodo None")

        try:
            return str(nodo.aceptar(self))
        except AttributeError:
            return str(nodo)

    def procesar(self, nodos: List[Any]) -> str:
        """
        Procesa una lista de nodos y retorna el código resultante.

        Args:
            nodos: Lista de nodos a procesar

        Returns:
            str: Código transpilado

        Raises:
            ValueError: Si la lista de nodos es None
        """
        if nodos is None:
            raise ValueError("La lista de nodos no puede ser None")

        self._output = []
        self.indent = 0

        try:
            for nodo in nodos:
                if nodo is not None:
                    nodo.aceptar(self)
        except Exception as e:
            raise ValueError(f"Error al procesar nodos: {str(e)}")

        return "\n".join(self._output)

    def reset(self) -> None:
        """Reinicia el estado del transpilador."""
        self._output = []
        self.indent = 0

    def get_output(self) -> List[str]:
        """
        Obtiene el resultado de la transpilación.

        Returns:
            List[str]: Lista de líneas generadas
        """
        return self._output.copy()
