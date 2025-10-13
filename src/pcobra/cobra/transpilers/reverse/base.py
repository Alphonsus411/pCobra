from abc import ABC, abstractmethod
from typing import List, Any
from pcobra.core.visitor import NodeVisitor

class BaseReverseTranspiler(NodeVisitor, ABC):
    """Clase base para transpiladores inversos que generan el AST de Cobra."""
    
    def __init__(self) -> None:
        super().__init__()
        self.ast: List[Any] = []

    @abstractmethod
    def generate_ast(self, code: str) -> List[Any]:
        """Genera el AST Cobra equivalente al código fuente dado.
        
        Args:
            code: Código fuente a transpillar
            
        Returns:
            Lista de nodos AST de Cobra
            
        Raises:
            NotImplementedError: Si no se implementa en la subclase
        """
        raise NotImplementedError
    
    def load_file(self, path: str) -> List[Any]:
        """Carga un archivo y genera su AST correspondiente.
        
        Args:
            path: Ruta al archivo a procesar
            
        Returns:
            Lista de nodos AST de Cobra
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            PermissionError: Si no hay permisos de lectura
            UnicodeDecodeError: Si hay error de codificación
        """
        try:
            with open(path, "r", encoding="utf-8") as archivo:
                contenido = archivo.read()
            return self.generate_ast(contenido)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            raise RuntimeError(f"Error al leer archivo {path}: {str(e)}")
