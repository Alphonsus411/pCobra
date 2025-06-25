"""Definiciones de los nodos del árbol de sintaxis abstracta de Cobra."""

from dataclasses import dataclass, field
from typing import Any, List, Optional

from src.cobra.lexico.lexer import Token

@dataclass
class NodoAST:
    """Clase base para todos los nodos del AST."""

    def aceptar(self, visitante):
        """Acepta un visitante y delega la operación a éste."""
        return visitante.visit(self)


@dataclass
class NodoAsignacion(NodoAST):
    variable: Any
    expresion: Any

    """Representa la asignación de una expresión a una variable."""

    def __post_init__(self):
        if isinstance(self.variable, Token):
            nombre = self.variable.valor
            self.identificador = str(nombre)
            self.variable = self.identificador
        else:
            nombre = self.variable
            self.identificador = nombre
            self.variable = nombre
        # Compatibilidad con pruebas antiguas
        self.nombre = self.identificador
        self.valor = self.expresion


@dataclass
class NodoHolobit(NodoAST):
    nombre: Optional[str] = None
    valores: Optional[List[Any]] = None

    """Define un holobit, una colección de valores numéricos."""

    def __post_init__(self):
        if self.valores is None and isinstance(self.nombre, list):
            self.valores = self.nombre
            self.nombre = None
        if self.valores is None:
            self.valores = []


@dataclass
class NodoCondicional(NodoAST):
    condicion: Any
    bloque_si: List[Any]
    bloque_sino: List[Any] = field(default_factory=list)

    """Bloque ``si`` opcionalmente acompañado de un bloque ``sino``."""


@dataclass
class NodoBucleMientras(NodoAST):
    condicion: Any
    cuerpo: List[Any]

    """Representa un bucle ``mientras`` con su condición y cuerpo."""


@dataclass
class NodoFor(NodoAST):
    variable: Any
    iterable: Any
    cuerpo: List[Any]

    """Estructura de control ``para`` que itera sobre un iterable."""


@dataclass
class NodoLista(NodoAST):
    elementos: List[Any]

    """Literal de lista de expresiones."""


@dataclass
class NodoDiccionario(NodoAST):
    elementos: Any

    """Literal de diccionario ``clave: valor``."""


@dataclass
class NodoDecorador(NodoAST):
    expresion: Any

    """Representa una línea de decorador previa a una función."""


@dataclass
class NodoFuncion(NodoAST):
    nombre: str
    parametros: List[str]
    cuerpo: List[Any]
    decoradores: List[Any] = field(default_factory=list)

    """Declaración de una función definida por el usuario."""


@dataclass
class NodoClase(NodoAST):
    nombre: str
    metodos: List[Any]
    bases: List[str] = field(default_factory=list)

    """Definición de una clase y sus métodos."""


@dataclass
class NodoMetodo(NodoAST):
    nombre: str
    parametros: List[str]
    cuerpo: List[Any]

    """Método perteneciente a una clase."""


@dataclass
class NodoInstancia(NodoAST):
    nombre_clase: str
    argumentos: List[Any] = field(default_factory=list)

    """Instanciación de una clase."""


@dataclass
class NodoAtributo(NodoAST):
    objeto: Any
    nombre: str

    """Acceso a un atributo de un objeto."""


@dataclass
class NodoLlamadaMetodo(NodoAST):
    objeto: Any
    nombre_metodo: str
    argumentos: List[Any] = field(default_factory=list)

    """Invocación de un método de un objeto."""


@dataclass
class NodoOperacionBinaria(NodoAST):
    izquierda: Any
    operador: Token
    derecha: Any

    """Operación que combina dos expresiones mediante un operador."""

    def __repr__(self):
        return f"({self.izquierda} {self.operador.valor} {self.derecha})"


@dataclass
class NodoOperacionUnaria(NodoAST):
    operador: Token
    operando: Any

    """Operación aplicada a un único operando."""

    def __repr__(self):
        return f"({self.operador.valor}{self.operando})"


@dataclass
class NodoValor(NodoAST):
    valor: Any

    """Representa un valor literal ya evaluado."""


@dataclass
class NodoIdentificador(NodoAST):
    nombre: str

    """Uso de una variable o identificador."""

    def __post_init__(self):
        self.valor = self.nombre

    def __repr__(self):
        return f"NodoIdentificador({self.nombre})"

    def evaluar(self, contexto):
        if self.nombre in contexto:
            return contexto[self.nombre]
        raise NameError(f"Identificador no definido: '{self.nombre}'")


@dataclass
class NodoLlamadaFuncion(NodoAST):
    nombre: str
    argumentos: List[Any]

    """Invocación de una función existente."""

    def __repr__(self):
        return f"NodoLlamadaFuncion(nombre={self.nombre}, argumentos={self.argumentos})"


@dataclass
class NodoHilo(NodoAST):
    llamada: NodoLlamadaFuncion

    """Ejecución de una llamada en un hilo separado."""

    def __repr__(self):
        return f"NodoHilo(llamada={self.llamada})"


@dataclass
class NodoRetorno(NodoAST):
    expresion: Any

    """Valor devuelto por una función."""

    def __repr__(self):
        return f"NodoRetorno(expresion={self.expresion})"


@dataclass
class NodoYield(NodoAST):
    expresion: Any

    """Expresión yield dentro de una función generadora."""

    def __repr__(self):
        return f"NodoYield(expresion={self.expresion})"


@dataclass
class NodoThrow(NodoAST):
    expresion: Any

    """Lanza una excepción durante la ejecución."""

    def __repr__(self):
        return f"NodoThrow(expresion={self.expresion})"


@dataclass
class NodoTryCatch(NodoAST):
    bloque_try: List[Any]
    nombre_excepcion: Optional[str] = None
    bloque_catch: List[Any] = field(default_factory=list)

    """Bloque ``try`` con manejo opcional de excepciones."""


@dataclass
class NodoImport(NodoAST):
    ruta: str

    """Importación de un módulo externo."""


@dataclass
class NodoUsar(NodoAST):
    modulo: str

    """Instrucción para usar un módulo especificado."""


@dataclass
class NodoPara(NodoAST):
    variable: Any
    iterable: Any
    cuerpo: List[Any]

    """Bucle ``para`` que itera sobre un iterable."""

    def __repr__(self):
        return (
            f"NodoPara(variable={self.variable}, iterable={self.iterable}, cuerpo={self.cuerpo})"
        )


@dataclass
class NodoImprimir(NodoAST):
    expresion: Any

    """Impresión de una expresión en la salida estándar."""

    def __repr__(self):
        return f"NodoImprimir(expresion={self.expresion})"


__all__ = [
    'NodoAST',
    'NodoAsignacion',
    'NodoHolobit',
    'NodoCondicional',
    'NodoBucleMientras',
    'NodoFor',
    'NodoLista',
    'NodoDiccionario',
    'NodoDecorador',
    'NodoFuncion',
    'NodoClase',
    'NodoMetodo',
    'NodoInstancia',
    'NodoAtributo',
    'NodoLlamadaMetodo',
    'NodoOperacionBinaria',
    'NodoOperacionUnaria',
    'NodoValor',
    'NodoIdentificador',
    'NodoLlamadaFuncion',
    'NodoHilo',
    'NodoRetorno',
    'NodoYield',
    'NodoThrow',
    'NodoTryCatch',
    'NodoImport',
    'NodoUsar',
    'NodoPara',
    'NodoImprimir',
]
