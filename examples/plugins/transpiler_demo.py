"""Transpilador de ejemplo para Cobra."""
from cobra.transpilers import BaseTranspiler


class TranspiladorDemo(BaseTranspiler):
    """Transpilador muy simple que genera un mensaje fijo."""
    
    def __init__(self):
        """Inicializa el transpilador."""
        super().__init__()
    
    def generate_code(self, nodos):
        """Genera el código a partir de los nodos del AST.
        
        Args:
            nodos: Árbol de sintaxis abstracta a procesar
            
        Returns:
            list: Lista con las líneas de código generadas
        """
        self.codigo = ["# Código generado por TranspiladorDemo"]
        return self.codigo
        
    def transpilar(self, nodos):
        """Transpila el código a partir de los nodos del AST.
        
        Args:
            nodos: Árbol de sintaxis abstracta a procesar
            
        Returns:
            list: Lista con las líneas de código generadas
        """
        return self.generate_code(nodos)