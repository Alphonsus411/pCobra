"""Transpilador de ejemplo para Cobra."""

from backend.src.cobra.transpilers.base import BaseTranspiler


class TranspiladorDemo(BaseTranspiler):
    """Transpilador muy simple que genera un mensaje fijo."""

    def generate_code(self, nodos):
        self.codigo = "# Código generado por TranspiladorDemo"
        return self.codigo

    def transpilar(self, nodos):
        return self.generate_code(nodos)
