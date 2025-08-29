from typing import List, Dict, Any
from core.ast_nodes import NodoMacro, NodoLlamadaFuncion

class MacroExpander:
    def __init__(self):
        self._macros: Dict[str, List[Any]] = {}
        self._expansion_depth = 0
        self.MAX_EXPANSION_DEPTH = 100
        
    def registrar_macro(self, nodo: NodoMacro) -> None:
        """Registra una macro validando su estructura."""
        if not nodo.nombre:
            raise ValueError("El nombre de la macro no puede estar vacío")
        if nodo.nombre in self._macros:
            raise ValueError(f"La macro '{nodo.nombre}' ya está definida")
        if not nodo.cuerpo:
            raise ValueError("El cuerpo de la macro no puede estar vacío")
        
        self._macros[nodo.nombre] = nodo.cuerpo
        
    def expandir_macros(self, nodos: List[Any]) -> List[Any]:
        """Expande macros en una lista de nodos con control de recursión."""
        self._expansion_depth += 1
        if self._expansion_depth > self.MAX_EXPANSION_DEPTH:
            raise RuntimeError("Profundidad máxima de expansión de macros excedida")
            
        try:
            return self._expandir_macros_interno(nodos)
        finally:
            self._expansion_depth -= 1
            
    def _expandir_macros_interno(self, nodos: List[Any]) -> List[Any]:
        """Implementación interna de la expansión de macros.
        :type self: object
        """
        resultado = []
        for nodo in nodos:
            if isinstance(nodo, NodoMacro):
                self.registrar_macro(nodo)
                continue
                
            # Expansión recursiva en atributos
            for atributo, valor in list(getattr(nodo, "__dict__", {}).items()):
                if isinstance(valor, list):
                    setattr(nodo, atributo, self.expandir_macros(valor))
                    
            if isinstance(nodo, NodoLlamadaFuncion) and nodo.nombre in self._macros:
                cuerpo = self._macros[nodo.nombre]
                resultado.extend(self.expandir_macros(cuerpo))
            else:
                resultado.append(nodo)
                
        return resultado
    
    def limpiar(self) -> None:
        """Limpia el estado del expansor de macros."""
        self._macros.clear()
        self._expansion_depth = 0


def expandir_macros(nodos: List[Any]) -> List[Any]:
    """Función de conveniencia que expande macros en una lista de nodos."""
    return MacroExpander().expandir_macros(nodos)