"""Definiciones de los nodos del árbol de sintaxis abstracta de Cobra."""

from dataclasses import dataclass, field
from reprlib import recursive_repr
from typing import Any, List, Optional, TYPE_CHECKING
import warnings

if TYPE_CHECKING:  # pragma: no cover - solo para verificación estática
    from pcobra.core.lexer import Token, TipoToken


@dataclass
class NodoAST:
    """Clase base para todos los nodos del AST."""

    def aceptar(self, visitante):
        """Acepta un visitante y delega la operación a éste."""
        return visitante.visit(self)


@dataclass
class NodoBloque(NodoAST):
    """Representa un bloque homogéneo de sentencias del AST."""

    instrucciones: List[NodoAST] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.instrucciones = list(self.instrucciones or [])

    def __iter__(self):
        return iter(self.instrucciones)

    def __len__(self):
        return len(self.instrucciones)

    def __getitem__(self, index):
        return self.instrucciones[index]

    def append(self, instruccion: NodoAST) -> None:
        self.instrucciones.append(instruccion)


def _asegurar_bloque(valor: Any) -> NodoBloque:
    if isinstance(valor, NodoBloque):
        return valor
    if isinstance(valor, list):
        return NodoBloque(valor)
    raise TypeError(f"Se esperaba NodoBloque o list, se recibió {type(valor).__name__}")


@dataclass
class NodoAsignacion(NodoAST):
    variable: Any
    expresion: Any
    inferencia: bool = False

    """Representa la asignación de una expresión a una variable."""

    def __post_init__(self):
        from pcobra.core.lexer import Token

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
    bloque_si: NodoBloque
    bloque_sino: NodoBloque = field(default_factory=NodoBloque)

    """Bloque ``si`` opcionalmente acompañado de un bloque ``sino``."""

    def __post_init__(self) -> None:
        self.bloque_si = _asegurar_bloque(self.bloque_si)
        self.bloque_sino = _asegurar_bloque(self.bloque_sino)


@dataclass
class NodoGarantia(NodoAST):
    condicion: Any
    bloque_continuacion: NodoBloque
    bloque_escape: NodoBloque

    """Sentencia ``garantia`` con bloque normal y de escape."""

    def __post_init__(self) -> None:
        self.bloque_continuacion = _asegurar_bloque(self.bloque_continuacion)
        self.bloque_escape = _asegurar_bloque(self.bloque_escape)


@dataclass
class NodoBucleMientras(NodoAST):
    condicion: Any
    cuerpo: NodoBloque

    """Representa un bucle ``mientras`` con su condición y cuerpo."""

    def __post_init__(self) -> None:
        self.cuerpo = _asegurar_bloque(self.cuerpo)


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
class NodoListaComprehension(NodoAST):
    expresion: Any
    variable: str
    iterable: Any
    condicion: Optional[Any] = None

    """Comprensión de listas ``[expresion para x en iterable si condicion]``."""


@dataclass
class NodoDiccionarioComprehension(NodoAST):
    clave: Any
    valor: Any
    variable: str
    iterable: Any
    condicion: Optional[Any] = None

    """Comprensión de diccionarios ``{clave: valor para x en iterable si condicion}``."""


@dataclass
class NodoListaTipo(NodoAST):
    nombre: str
    tipo: str
    elementos: List[Any] = field(default_factory=list)

    """Declaración de una lista con tipo explícito."""


@dataclass
class NodoDiccionarioTipo(NodoAST):
    nombre: str
    tipo_clave: str
    tipo_valor: str
    elementos: List[tuple[Any, Any]] = field(default_factory=list)

    """Declaración de un diccionario con tipos para clave y valor."""


@dataclass
class NodoTipo(NodoAST):
    """Representa una referencia a un tipo con soporte para genéricos."""

    nombre: Any
    genericos: List[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        from pcobra.core.lexer import Token

        if isinstance(self.nombre, NodoTipo):  # Compatibilidad con construcciones anidadas
            self.genericos = list(self.nombre.genericos)
            self.nombre = self.nombre.nombre
        if isinstance(self.nombre, Token):
            self.nombre = self.nombre.valor
        self.nombre = str(self.nombre)
        self.genericos = list(self.genericos)

    def __repr__(self) -> str:
        genericos = f", genericos={self.genericos!r}" if self.genericos else ""
        return f"NodoTipo(nombre={self.nombre!r}{genericos})"


@dataclass
class NodoDecorador(NodoAST):
    expresion: Any

    """Representa una línea de decorador previa a una función."""


@dataclass
class NodoFuncion(NodoAST):
    nombre: str
    parametros: List[str]
    cuerpo: NodoBloque
    decoradores: List[Any] = field(default_factory=list)
    asincronica: bool = False
    type_params: List[str] = field(default_factory=list)
    nombre_original: Optional[str] = None

    """Declaración de una función definida por el usuario."""

    def __post_init__(self) -> None:
        self.cuerpo = _asegurar_bloque(self.cuerpo)

@dataclass
class NodoMetodoAbstracto(NodoAST):
    nombre: str
    parametros: List[str] = field(default_factory=list)

    """Firma de un método sin implementación."""


@dataclass
class NodoInterface(NodoAST):
    nombre: str
    metodos: List[NodoMetodoAbstracto] = field(default_factory=list)

    """Declaración de una interfaz con métodos abstractos."""


@dataclass
class NodoClase(NodoAST):
    nombre: str
    metodos: List[Any]
    bases: List[str] = field(default_factory=list)
    type_params: List[str] = field(default_factory=list)

    """Definición de una clase y sus métodos."""


@dataclass
class NodoEnum(NodoAST):
    nombre: str
    miembros: List[str]

    """Declaración de un ``enum`` con sus miembros."""


@dataclass
class NodoMetodo(NodoAST):
    nombre: str
    parametros: List[str]
    cuerpo: NodoBloque
    asincronica: bool = False
    type_params: List[str] = field(default_factory=list)
    nombre_original: Optional[str] = None

    """Método perteneciente a una clase."""

    def __post_init__(self) -> None:
        self.cuerpo = _asegurar_bloque(self.cuerpo)


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
    operador: 'Token'
    derecha: Any

    """Operación que combina dos expresiones mediante un operador."""

    @recursive_repr(fillvalue="...")
    def __repr__(self):
        return f"({self.izquierda} {self.operador.valor} {self.derecha})"


@dataclass
class NodoOperacionUnaria(NodoAST):
    operador: 'Token'
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
        from pcobra.core.lexer import Token

        if isinstance(self.nombre, Token):
            self.nombre = self.nombre.valor
        elif isinstance(self.nombre, NodoIdentificador):
            self.nombre = self.nombre.nombre
        self.valor = self.nombre

    def __repr__(self):
        return f"NodoIdentificador({self.nombre})"

    def evaluar(self, contexto):
        warnings.warn(
            "NodoIdentificador.evaluar está deprecado; use "
            "InterpretadorCobra._resolver_identificador.",
            DeprecationWarning,
            stacklevel=2,
        )
        resolvedor = getattr(contexto, "_resolver_identificador", None)
        if callable(resolvedor):
            return resolvedor(self.nombre)

        if self.nombre not in contexto:
            raise NameError(f"Identificador no definido: '{self.nombre}'")
        return contexto[self.nombre]


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
class NodoDefer(NodoAST):
    expresion: Any
    linea: Optional[int] = None
    columna: Optional[int] = None

    """Sentencia que difiere la ejecución de una expresión."""

    def __repr__(self):
        return (
            f"NodoDefer(expresion={self.expresion}, linea={self.linea}, "
            f"columna={self.columna})"
        )


@dataclass
class NodoYield(NodoAST):
    expresion: Any

    """Expresión yield dentro de una función generadora."""

    def __repr__(self):
        return f"NodoYield(expresion={self.expresion})"


@dataclass
class NodoEsperar(NodoAST):
    expresion: Any

    """Expresión await utilizada en funciones asíncronas."""

    def __repr__(self):
        return f"NodoEsperar(expresion={self.expresion})"


@dataclass
class NodoOption(NodoAST):
    valor: Any | None = None

    """Representa un valor opcional, equivalente a ``Some`` o ``None``."""

    def __repr__(self):
        return "NodoOption(None)" if self.valor is None else f"NodoOption({self.valor})"


@dataclass
class NodoRomper(NodoAST):
    """Sentencia para romper un bucle."""

    def __repr__(self):
        return "NodoRomper()"


@dataclass
class NodoContinuar(NodoAST):
    """Sentencia para continuar con la siguiente iteración de un bucle."""

    def __repr__(self):
        return "NodoContinuar()"


@dataclass
class NodoPasar(NodoAST):
    """Sentencia vacía que no realiza ninguna acción."""

    def __repr__(self):
        return "NodoPasar()"


@dataclass
class NodoAssert(NodoAST):
    condicion: Any
    mensaje: Any | None = None


@dataclass
class NodoDel(NodoAST):
    objetivo: Any


@dataclass
class NodoGlobal(NodoAST):
    nombres: List[str]


@dataclass
class NodoNoLocal(NodoAST):
    nombres: List[str]


@dataclass
class NodoLambda(NodoAST):
    parametros: List[str]
    cuerpo: Any


@dataclass
class NodoWith(NodoAST):
    contexto: Any
    alias: str | None
    cuerpo: NodoBloque
    asincronico: bool = False

    def __post_init__(self) -> None:
        self.cuerpo = _asegurar_bloque(self.cuerpo)

    def __repr__(self):
        return (
            "NodoWith("
            f"contexto={self.contexto}, "
            f"alias={self.alias}, "
            f"cuerpo={self.cuerpo}, "
            f"asincronico={self.asincronico})"
        )


@dataclass
class NodoThrow(NodoAST):
    expresion: Any

    """Lanza una excepción durante la ejecución."""

    def __repr__(self):
        return f"NodoThrow(expresion={self.expresion})"


@dataclass
class NodoTryCatch(NodoAST):
    bloque_try: NodoBloque
    nombre_excepcion: Optional[str] = None
    bloque_catch: NodoBloque = field(default_factory=NodoBloque)
    bloque_finally: NodoBloque = field(default_factory=NodoBloque)

    """Bloque ``try`` con manejo opcional de excepciones."""

    def __post_init__(self) -> None:
        self.bloque_try = _asegurar_bloque(self.bloque_try)
        self.bloque_catch = _asegurar_bloque(self.bloque_catch)
        self.bloque_finally = _asegurar_bloque(self.bloque_finally)


@dataclass
class NodoImport(NodoAST):
    ruta: str

    """Importación de un módulo externo."""


@dataclass
class NodoUsar(NodoAST):
    modulo: str

    """Instrucción para usar un módulo especificado."""


@dataclass
class NodoImportDesde(NodoAST):
    modulo: str
    nombre: str
    alias: str | None = None


@dataclass
class NodoExport(NodoAST):
    nombre: str

    """Indica que un identificador debe exportarse en el módulo generado."""

    def __repr__(self):
        return f"NodoExport(nombre={self.nombre})"


@dataclass
class NodoPara(NodoAST):
    variable: Any
    iterable: Any
    cuerpo: NodoBloque
    asincronico: bool = False

    """Bucle ``para`` que itera sobre un iterable."""

    def __post_init__(self) -> None:
        self.cuerpo = _asegurar_bloque(self.cuerpo)

    def __repr__(self):
        return (
            "NodoPara("
            f"variable={self.variable}, "
            f"iterable={self.iterable}, "
            f"cuerpo={self.cuerpo}, "
            f"asincronico={self.asincronico})"
        )


@dataclass
class NodoProyectar(NodoAST):
    holobit: Any
    modo: Any

    """Proyección de un ``holobit`` en un modo específico."""


@dataclass
class NodoTransformar(NodoAST):
    holobit: Any
    operacion: Any
    parametros: List[Any] = field(default_factory=list)

    """Transformación aplicada a un ``holobit``."""


@dataclass
class NodoGraficar(NodoAST):
    holobit: Any

    """Visualización de un ``holobit``."""


@dataclass
class NodoImprimir(NodoAST):
    expresion: Any

    """Impresión de una expresión en la salida estándar."""

    @recursive_repr(fillvalue="...")
    def __repr__(self):
        return f"NodoImprimir(expresion={self.expresion})"


@dataclass
class NodoMacro(NodoAST):
    nombre: str
    cuerpo: NodoBloque

    """Representa una macro que almacena un conjunto de nodos a expandir."""

    def __post_init__(self) -> None:
        self.cuerpo = _asegurar_bloque(self.cuerpo)

    def __repr__(self):
        return f"NodoMacro(nombre={self.nombre}, cuerpo={list(self.cuerpo)})"


@dataclass
class NodoPattern(NodoAST):
    valor: Any


@dataclass
class NodoGuard(NodoAST):
    patron: NodoPattern
    condicion: Any


@dataclass
class NodoCase(NodoAST):
    valor: Any
    cuerpo: NodoBloque

    def __post_init__(self) -> None:
        self.cuerpo = _asegurar_bloque(self.cuerpo)


@dataclass
class NodoSwitch(NodoAST):
    expresion: Any
    casos: List[NodoCase]
    por_defecto: NodoBloque = field(default_factory=NodoBloque)

    def __post_init__(self) -> None:
        self.por_defecto = _asegurar_bloque(self.por_defecto)


__all__ = [
    "NodoAST",
    "NodoBloque",
    "NodoAsignacion",
    "NodoHolobit",
    "NodoCondicional",
    "NodoGarantia",
    "NodoBucleMientras",
    "NodoFor",
    "NodoLista",
    "NodoDiccionario",
    "NodoListaTipo",
    "NodoDiccionarioTipo",
    "NodoTipo",
    "NodoDecorador",
    "NodoFuncion",
    "NodoMetodoAbstracto",
    "NodoInterface",
    "NodoClase",
    "NodoEnum",
    "NodoMetodo",
    "NodoInstancia",
    "NodoAtributo",
    "NodoLlamadaMetodo",
    "NodoOperacionBinaria",
    "NodoOperacionUnaria",
    "NodoValor",
    "NodoIdentificador",
    "NodoLlamadaFuncion",
    "NodoHilo",
    "NodoRetorno",
    "NodoDefer",
    "NodoYield",
    "NodoEsperar",
    "NodoOption",
    "NodoRomper",
    "NodoContinuar",
    "NodoPasar",
    "NodoAssert",
    "NodoDel",
    "NodoGlobal",
    "NodoNoLocal",
    "NodoLambda",
    "NodoWith",
    "NodoThrow",
    "NodoTryCatch",
    "NodoImportDesde",
    "NodoExport",
    "NodoImport",
    "NodoUsar",
    "NodoPara",
    "NodoProyectar",
    "NodoTransformar",
    "NodoGraficar",
    "NodoImprimir",
    "NodoMacro",
    "NodoPattern",
    "NodoGuard",
    "NodoCase",
    "NodoSwitch",
]


class NodoDeclaracion:
    pass


class NodoModulo:
    pass


class NodoExpresion:
    pass
