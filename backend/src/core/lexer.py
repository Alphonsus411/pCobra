import logging
import re


class LexerError(Exception):
    """Excepción lanzada cuando el lexer encuentra un token inválido."""

    def __init__(self, mensaje: str, linea: int, columna: int) -> None:
        super().__init__(mensaje)
        self.linea = linea
        self.columna = columna


class TipoToken:
    DIVIDIR = 'DIVIDIR'
    MULTIPLICAR = 'MULTIPLICAR'
    CLASE = 'CLASE'
    DICCIONARIO = 'DICCIONARIO'
    LISTA = 'LISTA'
    RBRACE = 'RBRACE'
    DEF = 'DEF'
    CLASS = 'CLASS'
    IN = 'IN'
    LBRACE = 'LBRACE'
    FOR = 'FOR'
    DOSPUNTOS = 'DOS PUNTOS'
    VAR = 'VAR'
    FUNC = 'FUNC'
    REL = 'REL'
    SI = 'SI'
    SINO = 'SINO'
    MIENTRAS = 'MIENTRAS'
    PARA = 'PARA'
    IMPORT = 'IMPORT'
    HOLOBIT = 'HOLOBIT'
    PROYECTAR = 'PROYECTAR'
    TRANSFORMAR = 'TRANSFORMAR'
    GRAFICAR = 'GRAFICAR'
    TRY = 'TRY'
    CATCH = 'CATCH'
    THROW = 'THROW'
    ENTERO = 'ENTERO'
    FLOTANTE = 'FLOTANTE'
    CADENA = 'CADENA'
    BOOLEANO = 'BOOLEANO'
    IDENTIFICADOR = 'IDENTIFICADOR'
    ASIGNAR = 'ASIGNAR'
    SUMA = 'SUMA'
    RESTA = 'RESTA'
    MULT = 'MULT'
    DIV = 'DIV'
    MAYORQUE = 'MAYORQUE'
    MAYORIGUAL = 'MAYORIGUAL'
    MENORIGUAL = 'MENORIGUAL'
    IGUAL = 'IGUAL'
    DIFERENTE = 'DIFERENTE'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    MOD = 'MOD'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    COMA = 'COMA'
    RETORNO = 'RETORNO'
    FIN = 'FIN'
    EOF = 'EOF'
    IMPRIMIR = 'IMPRIMIR'  # Añadido soporte para 'imprimir'
    HILO = 'HILO'


class Token:
    def __init__(self, tipo, valor, linea: int | None = None, columna: int | None = None):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def __repr__(self):
        pos = f" @ {self.linea}:{self.columna}" if self.linea is not None else ""
        return f'Token({self.tipo}: {self.valor}{pos})'


class Lexer:
    def __init__(self, codigo_fuente):
        self.codigo_fuente = codigo_fuente
        self.posicion = 0
        self.tokens = []

    def tokenizar(self):
        # Elimina comentarios de una línea y bloques de comentarios
        codigo_sin_bloques = re.sub(r'/\*.*?\*/', '', self.codigo_fuente, flags=re.DOTALL)
        codigo_sin_doble = re.sub(r'//.*?$', '', codigo_sin_bloques, flags=re.MULTILINE)
        codigo_limpio = re.sub(r'#.*?$', '', codigo_sin_doble, flags=re.MULTILINE)

        self.codigo_fuente = codigo_limpio
        self.posicion = 0

        especificacion_tokens = [
            (TipoToken.VAR, r'\bvar\b'),
            (TipoToken.FUNC, r'\bfunc\b'),
            (TipoToken.FUNC, r'\b(func|definir)\b'),
            (TipoToken.REL, r'\brel\b'),
            (TipoToken.SI, r'\bsi\b'),
            (TipoToken.SINO, r'\bsino\b'),
            (TipoToken.MIENTRAS, r'\bmientras\b'),
            (TipoToken.PARA, r'\bpara\b'),
            (TipoToken.IMPORT, r'\bimport\b'),
            (TipoToken.HILO, r'\bhilo\b'),
            (TipoToken.IN, r'\bin\b'),  # Define el token 'in'
            (TipoToken.HOLOBIT, r'\bholobit\b'),
            (TipoToken.PROYECTAR, r'\bproyectar\b'),
            (TipoToken.TRANSFORMAR, r'\btransformar\b'),
            (TipoToken.GRAFICAR, r'\bgraficar\b'),
            (TipoToken.TRY, r'\btry\b'),
            (TipoToken.CATCH, r'\bcatch\b'),
            (TipoToken.THROW, r'\bthrow\b'),
            (TipoToken.IMPRIMIR, r'\bimprimir\b'),  # Reconoce 'imprimir'
            (TipoToken.FLOTANTE, r'\d+\.\d+'),
            (TipoToken.ENTERO, r'\d+'),
            (TipoToken.CADENA, r"'[^']*'|\"[^\"]*\""),
            (TipoToken.BOOLEANO, r'\b(verdadero|falso)\b'),
            (TipoToken.DOSPUNTOS, r':'),
            (TipoToken.FIN, r'\bfin\b'),
            (TipoToken.IDENTIFICADOR, r'[^\W\d_][\w]*'),
            (TipoToken.MAYORIGUAL, r'>='),
            (TipoToken.MENORIGUAL, r'<='),
            (TipoToken.IGUAL, r'=='),
            (TipoToken.DIFERENTE, r'!='),
            (TipoToken.AND, r'&&'),
            (TipoToken.OR, r'\|\|'),
            (TipoToken.NOT, r'!'),
            (TipoToken.MOD, r'%'),
            (TipoToken.ASIGNAR, r'='),
            (TipoToken.SUMA, r'\+'),
            (TipoToken.RESTA, r'-'),
            (TipoToken.MULT, r'\*'),
            (TipoToken.DIV, r'/'),
            (TipoToken.MAYORQUE, r'>'),
            (TipoToken.LPAREN, r'\('),
            (TipoToken.RPAREN, r'\)'),
            (TipoToken.LBRACKET, r'\['),
            (TipoToken.RBRACKET, r'\]'),
            (TipoToken.COMA, r','),
            (TipoToken.RETORNO, r'\bretorno\b'),
            (None, r'\s+'),  # Ignorar espacios en blanco
        ]

        prev_pos = -1
        same_pos_count = 0
        linea = 1
        columna = 1

        while self.posicion < len(self.codigo_fuente):
            matched = False
            for tipo, patron in especificacion_tokens:
                regex = re.compile(patron, re.UNICODE)
                coincidencia = regex.match(self.codigo_fuente[self.posicion:])
                if coincidencia:
                    valor_original = coincidencia.group(0)
                    if tipo:
                        valor = valor_original
                        logging.debug(
                            f"Token identificado: {tipo}, valor: '{valor}', "
                            f"posición: {self.posicion}"
                        )

                        if tipo == TipoToken.FLOTANTE:
                            valor = float(valor)
                        elif tipo == TipoToken.ENTERO:
                            valor = int(valor)
                        elif tipo == TipoToken.CADENA:
                            valor = valor[1:-1]
                        self.tokens.append(Token(tipo, valor, linea, columna))

                    # Actualizar posición
                    self.posicion += len(valor_original)
                    for ch in valor_original:
                        if ch == "\n":
                            linea += 1
                            columna = 1
                        else:
                            columna += 1
                    matched = True
                    break

            if not matched:
                error_token = self.codigo_fuente[self.posicion]
                logging.error(
                    f"Error: Token no reconocido en posición {self.posicion}: '{error_token}'"
                )
                raise LexerError(f"Token no reconocido: '{error_token}'", linea, columna)

            if self.posicion == prev_pos:
                same_pos_count += 1
                if same_pos_count > 5:
                    logging.error(
                        f"Bucle infinito detectado en posición {self.posicion}."
                    )
                    raise RuntimeError("Bucle infinito detectado en el lexer.")
            else:
                same_pos_count = 0

            prev_pos = self.posicion

        # Añade un token EOF al final para indicar el fin del código fuente
        self.tokens.append(Token(TipoToken.EOF, None, linea, columna))

        return self.tokens

    def analizar_token(self):
        """Mantiene compatibilidad con versiones previas."""
        return self.tokenizar()
