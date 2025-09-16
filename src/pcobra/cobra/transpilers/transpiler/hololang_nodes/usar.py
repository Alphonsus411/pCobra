"""Instrucción ``usar`` para Hololang."""


def visit_usar(self, nodo):
    """Transpila la instrucción ``usar`` a una directiva ``use`` de Hololang."""
    self.agregar_linea(f"use {nodo.modulo};")
