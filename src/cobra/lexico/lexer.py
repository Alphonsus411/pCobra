"""Analizador léxico para el lenguaje Cobra."""
import logging
import re
from enum import Enum
from typing import Dict, List, Optional, Pattern, Tuple, Union, cast

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LexerError(Exception):
    """Excepción base para errores del analizador léxico."""
    def __init__(self, mensaje: str, linea: int, columna: int) -> None:
        super().__init__(mensaje)
        self.linea = linea
        self.columna = columna

class InvalidTokenError(LexerError):
    """Excepción para símbolos no reconocidos."""
    pass

class UnclosedStringError(LexerError):
    """Excepción para cadenas sin cerrar."""
    pass

class TipoToken(Enum):
    """Enumeración de todos los tipos de tokens soportados."""
    DIVIDIR = "DIVIDIR"
    MULTIPLICAR = "MULTIPLICAR"
    CLASE = "CLASE"
    DICCIONARIO = "DICCIONARIO"
    LISTA = "LISTA"
    RBRACE = "RBRACE"
    DEF = "DEF"
    IN = "IN"
    LBRACE = "LBRACE"
    FOR = "FOR"
    DOSPUNTOS = "DOSPUNTOS"
    VAR = "VAR"
    FUNC = "FUNC"
    METODO = "METODO"
    ATRIBUTO = "ATRIBUTO"
    SI = "SI"
    SINO = "SINO"
    MIENTRAS = "MIENTRAS"
    PARA = "PARA"
    IMPORT = "IMPORT"
    USAR = "USAR"
    MACRO = "MACRO"
    HOLOBIT = "HOLOBIT"
    PROYECTAR = "PROYECTAR"
    TRANSFORMAR = "TRANSFORMAR"
    GRAFICAR = "GRAFICAR"
    TRY = "TRY"
    CATCH = "CATCH"
    THROW = "THROW"
    INTENTAR = "INTENTAR"
    CAPTURAR = "CAPTURAR"
    LANZAR = "LANZAR"
    ENTERO = "ENTERO"
    FLOTANTE = "FLOTANTE"
    CADENA = "CADENA"
    BOOLEANO = "BOOLEANO"
    IDENTIFICADOR = "IDENTIFICADOR"
    ASIGNAR = "ASIGNAR"
    SUMA = "SUMA"
    RESTA = "RESTA"
    MULT = "MULT"
    DIV = "DIV"
    # Los tokens de comparación también se usan como delimitadores de tipos genéricos
    MAYORQUE = "MAYORQUE"
    MENORQUE = "MENORQUE"
    MAYORIGUAL = "MAYORIGUAL"
    MENORIGUAL = "MENORIGUAL"
    IGUAL = "IGUAL"
    DIFERENTE = "DIFERENTE"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    MOD = "MOD"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMA = "COMA"
    RETORNO = "RETORNO"
    FIN = "FIN"
    EOF = "EOF"
    IMPRIMIR = "IMPRIMIR"
    HILO = "HILO"
    ASINCRONICO = "ASINCRONICO"
    DECORADOR = "DECORADOR"
    YIELD = "YIELD"
    ESPERAR = "ESPERAR"
    ROMPER = "ROMPER"
    CONTINUAR = "CONTINUAR"
    PASAR = "PASAR"
    AFIRMAR = "AFIRMAR"
    ELIMINAR = "ELIMINAR"
    GLOBAL = "GLOBAL"
    NOLOCAL = "NOLOCAL"
    LAMBDA = "LAMBDA"
    CON = "CON"
    FINALMENTE = "FINALMENTE"
    DESDE = "DESDE"
    COMO = "COMO"
    SWITCH = "SWITCH"
    CASE = "CASE"
    VARIABLE = "VARIABLE"
    ASIGNAR_INFERENCIA = "ASIGNAR_INFERENCIA"

class Token:
    """Representa un token del lenguaje con su tipo, valor y posición."""
    def __init__(
        self, 
        tipo: TipoToken,
        valor: Optional[Union[str, int, float]],
        linea: Optional[int] = None,
        columna: Optional[int] = None
    ) -> None:
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def __repr__(self) -> str:
        pos = f" @ {self.linea}:{self.columna}" if self.linea is not None else ""
        return f"Token({self.tipo}: {self.valor}{pos})"

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Token):
            return NotImplemented
        return (self.tipo == otro.tipo and 
                self.valor == otro.valor and 
                self.linea == otro.linea and 
                self.columna == otro.columna)


class EstadoLexer:
    """Mantiene el estado del lexer para permitir retroceso."""
    def __init__(self, posicion: int, linea: int, columna: int) -> None:
        self.posicion = posicion
        self.linea = linea
        self.columna = columna

    def __repr__(self) -> str:
        return f"EstadoLexer(pos={self.posicion}, lin={self.linea}, col={self.columna})"

class Lexer:
    """Analizador léxico para el lenguaje Cobra."""

    # Constantes para patrones de tokens
    PATRON_COMENTARIOS = re.compile(
        r"/\*.*?\*/|//.*?$|#.*?$",
        flags=re.DOTALL | re.MULTILINE | re.UNICODE
    )

    MAX_ITERACIONES = 1000000  # Límite de seguridad para bucles

    def __init__(self, codigo_fuente: str) -> None:
        """Inicializa el analizador léxico.

        Args:
            codigo_fuente: Código fuente a analizar

        Raises:
            TypeError: Si el código fuente no es una cadena
        """
        if not isinstance(codigo_fuente, str):
            raise TypeError("El código fuente debe ser una cadena de texto")
        
        self.codigo_fuente = codigo_fuente
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.tokens: List[Token] = []
        self._cache: Dict[str, List[Token]] = {}
        self._inicializar_especificaciones()

    def _inicializar_especificaciones(self) -> None:
        """Inicializa las especificaciones de tokens con sus patrones."""
        self.especificacion_tokens: List[Tuple[Optional[TipoToken], Pattern[str]]] = [
            (TipoToken.VAR, re.compile(r"\bvar\b")),
            (TipoToken.VARIABLE, re.compile(r"\bvariable\b")),
            (TipoToken.FUNC, re.compile(r"\b(func|definir)\b")),
            (TipoToken.METODO, re.compile(r"\bmetodo\b")),
            (TipoToken.ATRIBUTO, re.compile(r"\batributo\b")),
            (TipoToken.SI, re.compile(r"\bsi\b")),
            (TipoToken.SINO, re.compile(r"\bsino\b")),
            (TipoToken.MIENTRAS, re.compile(r"\bmientras\b")),
            (TipoToken.PARA, re.compile(r"\bpara\b")),
            (TipoToken.IMPORT, re.compile(r"\bimport\b")),
            (TipoToken.USAR, re.compile(r"\busar\b")),
            (TipoToken.MACRO, re.compile(r"\bmacro\b")),
            (TipoToken.HILO, re.compile(r"\bhilo\b")),
            (TipoToken.ASINCRONICO, re.compile(r"\basincronico\b")),
            (TipoToken.SWITCH, re.compile(r"\b(switch|segun)\b")),
            (TipoToken.CASE, re.compile(r"\b(case|caso)\b")),
            (TipoToken.CLASE, re.compile(r"\bclase\b")),
            (TipoToken.IN, re.compile(r"\bin\b")),
            (TipoToken.HOLOBIT, re.compile(r"\bholobit\b")),
            (TipoToken.PROYECTAR, re.compile(r"\bproyectar\b")),
            (TipoToken.TRANSFORMAR, re.compile(r"\btransformar\b")),
            (TipoToken.GRAFICAR, re.compile(r"\bgraficar\b")),
            (TipoToken.TRY, re.compile(r"\btry\b")),
            (TipoToken.CATCH, re.compile(r"\bcatch\b")),
            (TipoToken.THROW, re.compile(r"\bthrow\b")),
            (TipoToken.INTENTAR, re.compile(r"\bintentar\b")),
            (TipoToken.CAPTURAR, re.compile(r"\bcapturar\b")),
            (TipoToken.LANZAR, re.compile(r"\blanzar\b")),
            (TipoToken.IMPRIMIR, re.compile(r"\bimprimir\b")),
            (TipoToken.YIELD, re.compile(r"\byield\b")),
            (TipoToken.ESPERAR, re.compile(r"\besperar\b")),
            (TipoToken.ROMPER, re.compile(r"\bromper\b")),
            (TipoToken.CONTINUAR, re.compile(r"\bcontinuar\b")),
            (TipoToken.PASAR, re.compile(r"\bpasar\b")),
            (TipoToken.AFIRMAR, re.compile(r"\bafirmar\b")),
            (TipoToken.ELIMINAR, re.compile(r"\beliminar\b")),
            (TipoToken.GLOBAL, re.compile(r"\bglobal\b")),
            (TipoToken.NOLOCAL, re.compile(r"\bnolocal\b")),
            (TipoToken.LAMBDA, re.compile(r"\blambda\b")),
            (TipoToken.CON, re.compile(r"\bcon\b")),
            (TipoToken.FINALMENTE, re.compile(r"\bfinalmente\b")),
            (TipoToken.DESDE, re.compile(r"\bdesde\b")),
            (TipoToken.COMO, re.compile(r"\bcomo\b")),
            (TipoToken.FLOTANTE, re.compile(r"\d+\.\d+")),
            (TipoToken.ENTERO, re.compile(r"\d+")),
            (TipoToken.CADENA, re.compile(r"'(?:\\.|[^'])*'|\"(?:\\.|[^\"])*\"")),
            (TipoToken.BOOLEANO, re.compile(r"\b(verdadero|falso)\b")),
            (TipoToken.ASIGNAR_INFERENCIA, re.compile(r":=")),
            (TipoToken.DOSPUNTOS, re.compile(r":")),
            (TipoToken.FIN, re.compile(r"\bfin\b")),
            (TipoToken.RETORNO, re.compile(r"\bretorno\b")),
            (TipoToken.IDENTIFICADOR, re.compile(r"[^\W\d][\w]*")),
            (TipoToken.MAYORIGUAL, re.compile(r">=")),
            (TipoToken.MENORIGUAL, re.compile(r"<=")),
            (TipoToken.IGUAL, re.compile(r"==")),
            (TipoToken.DIFERENTE, re.compile(r"!=")),
            (TipoToken.AND, re.compile(r"&&")),
            (TipoToken.OR, re.compile(r"\|\|")),
            (TipoToken.NOT, re.compile(r"!")),
            (TipoToken.MOD, re.compile(r"%")),
            (TipoToken.ASIGNAR, re.compile(r"=")),
            (TipoToken.SUMA, re.compile(r"\+")),
            (TipoToken.RESTA, re.compile(r"-")),
            (TipoToken.MULT, re.compile(r"\*")),
            (TipoToken.DIV, re.compile(r"/")),
            # Símbolos genéricos '<' y '>' también actúan como operadores de comparación
            (TipoToken.MAYORQUE, re.compile(r">")),
            (TipoToken.MENORQUE, re.compile(r"<")),
            (TipoToken.LPAREN, re.compile(r"\(")),
            (TipoToken.RPAREN, re.compile(r"\)")),
            (TipoToken.LBRACE, re.compile(r"\{")),
            (TipoToken.RBRACE, re.compile(r"\}")),
            (TipoToken.LBRACKET, re.compile(r"\[")),
            (TipoToken.RBRACKET, re.compile(r"\]")),
            (TipoToken.COMA, re.compile(r",")),
            (TipoToken.DECORADOR, re.compile(r"@")),
            (None, re.compile(r"\s+"))  # Ignorar espacios en blanco
        ]

    def _limpiar_comentarios(self) -> None:
        """Elimina todos los tipos de comentarios del código fuente."""
        self.codigo_fuente = self.PATRON_COMENTARIOS.sub("", self.codigo_fuente)

    def _procesar_cadena(self, valor: str) -> str:
        """Procesa una cadena, manejando caracteres de escape.

        Args:
            valor: Cadena a procesar (incluyendo comillas)

        Returns:
            str: Cadena procesada sin comillas

        Raises:
            UnclosedStringError: Si la cadena está mal formada
        """
        try:
            return bytes(valor[1:-1], "utf-8").decode("unicode_escape")
        except UnicodeError as e:
            raise UnclosedStringError(
                f"Cadena mal formada: {str(e)}",
                self.linea,
                self.columna
            )

    def _actualizar_posicion(self, texto: str) -> None:
        """Actualiza la posición del lexer después de consumir un token.

        Args:
            texto: Texto consumido
        """
        for ch in texto:
            if ch == "\n":
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1
        self.posicion += len(texto)

    def _procesar_valor(
        self, 
        tipo: TipoToken, 
        valor: str
    ) -> Union[str, int, float]:
        """Procesa el valor del token según su tipo.

        Args:
            tipo: Tipo del token
            valor: Valor original del token

        Returns:
            Valor procesado según el tipo
        """
        if tipo == TipoToken.FLOTANTE:
            return float(valor)
        elif tipo == TipoToken.ENTERO:
            return int(valor)
        elif tipo == TipoToken.CADENA:
            return self._procesar_cadena(valor)
        elif tipo == TipoToken.BOOLEANO:
            return valor == "verdadero"
        return valor

    def _manejar_error(self) -> None:
        """Maneja errores de tokenización.

        Raises:
            UnclosedStringError: Para cadenas sin cerrar
            InvalidTokenError: Para otros tokens inválidos
        """
        error_token = self.codigo_fuente[self.posicion]
        if error_token in {"'", '"'}:
            raise UnclosedStringError(
                f"Cadena sin cerrar en línea {self.linea}, columna {self.columna}",
                self.linea,
                self.columna
            )
        raise InvalidTokenError(
            f"Token no reconocido: '{error_token}' en línea {self.linea}, "
            f"columna {self.columna}",
            self.linea,
            self.columna
        )

    def _tokenizar_base(self) -> List[Token]:
        """Implementación base del proceso de tokenización.

        Returns:
            Lista de tokens encontrados

        Raises:
            RuntimeError: Si se excede el límite de iteraciones
        """
        self._limpiar_comentarios()
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []

        iteraciones = 0

        while self.posicion < len(self.codigo_fuente):
            if iteraciones > self.MAX_ITERACIONES:
                raise RuntimeError("Se excedió el límite de iteraciones")
            
            matched = False
            for tipo, regex in self.especificacion_tokens:
                coincidencia = regex.match(self.codigo_fuente[self.posicion:])
                if coincidencia:
                    valor_original = coincidencia.group(0)
                    if tipo:
                        valor = self._procesar_valor(tipo, valor_original)
                        token = Token(tipo, valor, self.linea, self.columna)
                        self.tokens.append(token)
                        logger.debug(
                            "Token identificado: %s, valor: '%s', posición: %d",
                            tipo,
                            valor,
                            self.posicion
                        )
                    self._actualizar_posicion(valor_original)
                    matched = True
                    break

            if not matched:
                self._manejar_error()
            
            iteraciones += 1

        # Añade token EOF
        self.tokens.append(Token(TipoToken.EOF, None, self.linea, self.columna))
        return self.tokens

    def tokenizar(
        self, 
        *, 
        incremental: bool = False, 
        profile: bool = False
    ) -> List[Token]:
        """Convierte el código en tokens.

        Args:
            incremental: Si se debe usar tokenización incremental
            profile: Si se debe perfilar el proceso

        Returns:
            Lista de tokens

        Raises:
            Exception: Si hay error en la tokenización
        """
        try:
            if incremental:
                return self._tokenizar_incremental()
            if profile:
                return self._tokenizar_con_perfil()
            return self._tokenizar_base()
        except Exception as e:
            logger.error("Error durante la tokenización: %s", str(e))
            raise

    def _tokenizar_incremental(self) -> List[Token]:
        """Implementa tokenización incremental usando caché.

        Returns:
            Lista de tokens
        """
        from core.ast_cache import obtener_tokens_fragmento
        self.tokens = []
        for linea in self.codigo_fuente.splitlines(keepends=True):
            if linea in self._cache:
                self.tokens.extend(self._cache[linea])
            else:
                tokens_linea = obtener_tokens_fragmento(linea)[:-1]
                self._cache[linea] = tokens_linea
                self.tokens.extend(tokens_linea)
        self.tokens.append(Token(TipoToken.EOF, None))
        return self.tokens

    def _tokenizar_con_perfil(self) -> List[Token]:
        """Ejecuta la tokenización con perfilado.

        Returns:
            Lista de tokens
        """
        import cProfile
        import pstats
        import io
        
        pr = cProfile.Profile()
        pr.enable()
        resultado = self._tokenizar_base()
        pr.disable()
        
        s = io.StringIO()
        stats = pstats.Stats(pr, stream=s)
        stats.sort_stats("cumulative").print_stats(5)
        logger.info("Lexer profile:\n%s", s.getvalue())
        
        return resultado

    def analizar_token(self) -> List[Token]:
        """Mantiene compatibilidad con versiones previas.

        Returns:
            Lista de tokens
        """
        return self.tokenizar()

    def guardar_estado(self) -> EstadoLexer:
        """Guarda el estado actual del lexer.

        Returns:
            EstadoLexer con la posición actual
        """
        return EstadoLexer(self.posicion, self.linea, self.columna)

    def restaurar_estado(self, estado: EstadoLexer) -> None:
        """Restaura el lexer a un estado anterior.

        Args:
            estado: Estado previo a restaurar
        """
        self.posicion = estado.posicion
        self.linea = estado.linea
        self.columna = estado.columna

    def peek(self) -> Optional[Token]:
        """Mira el siguiente token sin consumirlo.

        Returns:
            El siguiente token o None si no hay más
        """
        estado = self.guardar_estado()
        try:
            token = self.siguiente_token()
            return token
        finally:
            self.restaurar_estado(estado)

    def siguiente_token(self) -> Optional[Token]:
        """Obtiene el siguiente token.

        Returns:
            El siguiente token o None si no hay más

        Raises:
            LexerError: Si hay un error al tokenizar
        """
        if not self.tokens:
            self._tokenizar_base()

        if self.posicion >= len(self.tokens):
            return None

        token = self.tokens[self.posicion]
        self.posicion += 1
        return token

    def retroceder(self) -> None:
        """Retrocede una posición en los tokens."""
        if self.posicion > 0:
            self.posicion -= 1

    def hay_mas_tokens(self) -> bool:
        """Verifica si quedan más tokens por procesar.

        Returns:
            True si hay más tokens, False en caso contrario
        """
        return self.posicion < len(self.tokens)

    def obtener_contexto(self, num_lineas: int = 3) -> str:
        """Obtiene el contexto alrededor de la posición actual.

        Args:
            num_lineas: Número de líneas de contexto

        Returns:
            Texto con el contexto
        """
        lineas = self.codigo_fuente.splitlines()
        if not lineas:
            return ""

        inicio = max(0, self.linea - num_lineas - 1)
        fin = min(len(lineas), self.linea + num_lineas)

        contexto = []
        for i in range(inicio, fin):
            marca = ">" if i == (self.linea - 1) else " "
            contexto.append(f"{marca} {i + 1:4d} | {lineas[i]}")
            if i == (self.linea - 1):
                contexto.append(" " * (self.columna + 7) + "^")

        return "\n".join(contexto)

    def reiniciar(self) -> None:
        """Reinicia el estado del lexer."""
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []
        self._cache.clear()

