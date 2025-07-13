from abc import ABC, abstractmethod
from core.visitor import NodeVisitor


class BaseTranspiler(NodeVisitor, ABC):
    """Clase base para los transpiladores de Cobra."""

    def __init__(self):
        self.codigo = []

    @abstractmethod
    def generate_code(self, ast):
        """Genera el código a partir del AST proporcionado."""
        raise NotImplementedError

    def save_file(self, path):
        """Guarda el código generado en la ruta dada."""
        contenido = "\n".join(self.codigo) if isinstance(self.codigo, list) else str(self.codigo)
        with open(path, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)
