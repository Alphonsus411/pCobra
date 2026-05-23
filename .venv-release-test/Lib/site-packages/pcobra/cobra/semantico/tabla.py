"""Estructuras de la tabla de símbolos y manejo jerárquico de ámbitos."""

from dataclasses import dataclass, field
from typing import Dict, Optional, Set, List


TIPOS_VALIDOS = {'variable', 'funcion', 'clase'}
MAX_PROFUNDIDAD_RESOLUCION = 100


@dataclass(frozen=True)
class Simbolo:
    """Representa un símbolo en la tabla de símbolos.
    
    Attributes:
        nombre: Nombre del símbolo
        tipo: Tipo del símbolo ('variable', 'funcion' o 'clase')
    """
    nombre: str
    tipo: str

    def __post_init__(self) -> None:
        """Valida los tipos y valores de los atributos."""
        if not isinstance(self.nombre, str):
            raise TypeError("El nombre debe ser una cadena")
        if not isinstance(self.tipo, str):
            raise TypeError("El tipo debe ser una cadena")
        if self.tipo not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo no válido. Debe ser uno de: {TIPOS_VALIDOS}")


class Ambito:
    """Representa un ámbito de visibilidad para los símbolos.
    
    Implementa un espacio de nombres jerárquico donde los símbolos pueden
    ser declarados y resueltos, considerando la anidación de ámbitos.
    """

    def __init__(self, padre: Optional['Ambito'] = None) -> None:
        """Inicializa un nuevo ámbito.
        
        Args:
            padre: Ámbito padre opcional del cual este ámbito hereda
        """
        self.padre = padre
        self.simbolos: Dict[str, Simbolo] = {}

    def declarar(self, nombre: str, tipo: str) -> None:
        """Declara un nuevo símbolo en el ámbito actual.
        
        Args:
            nombre: Nombre del símbolo a declarar
            tipo: Tipo del símbolo ('variable', 'funcion' o 'clase')
            
        Raises:
            TypeError: Si nombre o tipo no son cadenas
            ValueError: Si el tipo no es válido o el símbolo ya existe
        """
        if not isinstance(nombre, str):
            raise TypeError("El nombre debe ser una cadena")
        if nombre in self.simbolos:
            raise ValueError(f"Símbolo ya declarado en este ámbito: {nombre}")
        self.simbolos[nombre] = Simbolo(nombre, tipo)

    def resolver(self, nombre: str, profundidad: int = 0) -> Optional[Simbolo]:
        """Busca un símbolo en este ámbito y ámbitos superiores.
        
        Args:
            nombre: Nombre del símbolo a buscar
            profundidad: Profundidad actual de la búsqueda recursiva
            
        Returns:
            El símbolo encontrado o None si no existe
            
        Raises:
            RecursionError: Si se excede la profundidad máxima de resolución
        """
        if profundidad > MAX_PROFUNDIDAD_RESOLUCION:
            raise RecursionError("Excedida profundidad máxima de resolución")
            
        if nombre in self.simbolos:
            return self.simbolos[nombre]
        if self.padre:
            return self.padre.resolver(nombre, profundidad + 1)
        return None

    def resolver_local(self, nombre: str) -> Optional[Simbolo]:
        """Busca un símbolo solo en el ámbito actual.
        
        Args:
            nombre: Nombre del símbolo a buscar
            
        Returns:
            El símbolo encontrado o None si no existe
        """
        return self.simbolos.get(nombre)
    
    def obtener_todos_simbolos(self) -> Set[Simbolo]:
        """Obtiene todos los símbolos accesibles desde este ámbito.
        
        Returns:
            Conjunto con todos los símbolos de este ámbito y ámbitos superiores
        """
        simbolos = set(self.simbolos.values())
        if self.padre:
            simbolos.update(self.padre.obtener_todos_simbolos())
        return simbolos
    
    def clonar(self, con_padre: bool = True) -> 'Ambito':
        """Crea una copia de este ámbito.
        
        Args:
            con_padre: Si True, clona también el ámbito padre
            
        Returns:
            Nueva instancia de Ambito con los mismos símbolos
        """
        nuevo = Ambito(self.padre if con_padre else None)
        nuevo.simbolos = self.simbolos.copy()
        return nuevo

    def __repr__(self) -> str:
        """Devuelve una representación en string del ámbito.
        
        Returns:
            Representación del ámbito para depuración
        """
        return f"Ambito(simbolos={self.simbolos})"