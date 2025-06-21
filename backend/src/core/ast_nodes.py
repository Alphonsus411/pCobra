from dataclasses import dataclass, field
from typing import Any, List, Optional

from .lexer import Token

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


@dataclass
class NodoBucleMientras(NodoAST):
    condicion: Any
    cuerpo: List[Any]


@dataclass
class NodoFor(NodoAST):
    variable: Any
    iterable: Any
    cuerpo: List[Any]


@dataclass
class NodoLista(NodoAST):
    elementos: List[Any]


@dataclass
class NodoDiccionario(NodoAST):
    elementos: Any


@dataclass
class NodoFuncion(NodoAST):
    nombre: str
    parametros: List[str]
    cuerpo: List[Any]


@dataclass
class NodoClase(NodoAST):
    nombre: str
    metodos: List[Any]


@dataclass
class NodoMetodo(NodoAST):
    nombre: str
    parametros: List[str]
    cuerpo: List[Any]


@dataclass
class NodoInstancia(NodoAST):
    nombre_clase: str
    argumentos: List[Any] = field(default_factory=list)


@dataclass
class NodoAtributo(NodoAST):
    objeto: Any
    nombre: str


@dataclass
class NodoLlamadaMetodo(NodoAST):
    objeto: Any
    nombre_metodo: str
    argumentos: List[Any] = field(default_factory=list)


@dataclass
class NodoOperacionBinaria(NodoAST):
    izquierda: Any
    operador: Token
    derecha: Any

    def __repr__(self):
        return f"({self.izquierda} {self.operador.valor} {self.derecha})"


@dataclass
class NodoOperacionUnaria(NodoAST):
    operador: Token
    operando: Any

    def __repr__(self):
        return f"({self.operador.valor}{self.operando})"


@dataclass
class NodoValor(NodoAST):
    valor: Any


@dataclass
class NodoIdentificador(NodoAST):
    nombre: str

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

    def __repr__(self):
        return f"NodoLlamadaFuncion(nombre={self.nombre}, argumentos={self.argumentos})"


@dataclass
class NodoHilo(NodoAST):
    llamada: NodoLlamadaFuncion

    def __repr__(self):
        return f"NodoHilo(llamada={self.llamada})"


@dataclass
class NodoRetorno(NodoAST):
    expresion: Any

    def __repr__(self):
        return f"NodoRetorno(expresion={self.expresion})"


@dataclass
class NodoThrow(NodoAST):
    expresion: Any

    def __repr__(self):
        return f"NodoThrow(expresion={self.expresion})"


@dataclass
class NodoTryCatch(NodoAST):
    bloque_try: List[Any]
    nombre_excepcion: Optional[str] = None
    bloque_catch: List[Any] = field(default_factory=list)


@dataclass
class NodoImport(NodoAST):
    ruta: str


@dataclass
class NodoPara(NodoAST):
    variable: Any
    iterable: Any
    cuerpo: List[Any]

    def __repr__(self):
        return (
            f"NodoPara(variable={self.variable}, iterable={self.iterable}, cuerpo={self.cuerpo})"
        )


@dataclass
class NodoImprimir(NodoAST):
    expresion: Any

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
    'NodoThrow',
    'NodoTryCatch',
    'NodoImport',
    'NodoPara',
    'NodoImprimir',
]
