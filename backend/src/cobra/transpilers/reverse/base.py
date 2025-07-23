from abc import ABC, abstractmethod
from core.visitor import NodeVisitor


class BaseReverseTranspiler(NodeVisitor, ABC):
    """Clase base para transpiladores inversos que generan el AST de Cobra."""

    def __init__(self):
        self.ast = []

    @abstractmethod
    def generate_ast(self, code: str):
        """Devuelve el AST Cobra equivalente al código fuente dado."""
        raise NotImplementedError

    def load_file(self, path: str):
        """Carga un archivo y genera su AST correspondiente."""
        with open(path, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
        return self.generate_ast(contenido)
