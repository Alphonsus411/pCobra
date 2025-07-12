"""Tipos de datos y operaciones para manipular holobits."""

import json


class Holobit:
    """Representa un conjunto de valores numericos para operaciones 3D/2D."""

    def __init__(self, valores):
        if not hasattr(valores, "__iter__"):
            raise TypeError("'valores' debe ser iterable")
        self.valores = [float(v) for v in valores]

    def __repr__(self):
        return f"Holobit({self.valores})"

    def __len__(self):
        return len(self.valores)

    def __getitem__(self, index):
        return self.valores[index]

    def to_json(self):
        """Convierte los valores del Holobit a una cadena JSON."""
        return json.dumps(self.valores)
