import re
import logging


class TipoToken:
    VAR = 'VAR'
    FUNC = 'FUNC'
    REL = 'REL'
    SI = 'SI'
    SINO = 'SINO'
    MIENTRAS = 'MIENTRAS'
    PARA = 'PARA'
    HOLOBIT = 'HOLOBIT'
    PROYECTAR = 'PROYECTAR'
    TRANSFORMAR = 'TRANSFORMAR'
    GRAFICAR = 'GRAFICAR'
    ENTERO = 'ENTERO'
    FLOTANTE = 'FLOTANTE'
    CADENA = 'CADENA'
    BOOLEANO = 'BOOLEANO'
    IDENTIFICADOR = 'IDENTIFICADOR'
    ASIGNAR = 'ASIGNAR'
    DOSPUNTOS = 'DOSPUNTOS'
    SUMA = 'SUMA'
    RESTA = 'RESTA'
    MULT = 'MULT'
    DIV = 'DIV'
    MAYORQUE = 'MAYORQUE'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    COMA = 'COMA'
    EOF = 'EOF'


class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor

    def __repr__(self):
        return f'Token({self.tipo}: {self.valor})'


class Lexer:
    def __init__(self, codigo_fuente):
        self.codigo_fuente = codigo_fuente
        self.posicion = 0
        self.tokens = []

    def tokenizar(self):
        especificacion_tokens = [
            (TipoToken.VAR, r'\bvar\b'),
            (TipoToken.FUNC, r'\bfunc\b'),
            (TipoToken.REL, r'\brel\b'),
            (TipoToken.SI, r'\bsi\b'),
            (TipoToken.SINO, r'\bsino\b'),
            (TipoToken.MIENTRAS, r'\bmientras\b'),
            (TipoToken.PARA, r'\bpara\b'),
            (TipoToken.HOLOBIT, r'\bholobit\b'),
            (TipoToken.PROYECTAR, r'\bproyectar\b'),
            (TipoToken.TRANSFORMAR, r'\btransformar\b'),
            (TipoToken.GRAFICAR, r'\bgraficar\b'),
            (TipoToken.FLOTANTE, r'\d+\.\d+'),
            (TipoToken.ENTERO, r'\d+'),
            (TipoToken.CADENA, r"'[^']*'|\"[^\"]*\""),
            (TipoToken.BOOLEANO, r'\b(verdadero|falso)\b'),
            (TipoToken.IDENTIFICADOR, r'[A-Za-z_][A-Za-z0-9_]*'),
            (TipoToken.ASIGNAR, r'='),  # Asignación
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
            (None, r'\s+'),  # Ignorar espacios en blanco
        ]

        while self.posicion < len(self.codigo_fuente):
            matched = False
            for tipo, patron in especificacion_tokens:
                regex = re.compile(patron)
                coincidencia = regex.match(self.codigo_fuente[self.posicion:])
                if coincidencia:
                    if tipo:
                        valor = coincidencia.group(0)
                        if tipo == TipoToken.FLOTANTE:
                            valor = float(valor)
                        elif tipo == TipoToken.ENTERO:
                            valor = int(valor)
                        self.tokens.append(Token(tipo, valor))
                    self.posicion += len(coincidencia.group(0))
                    matched = True
                    break

            if not matched:
                error_token = self.codigo_fuente[self.posicion:self.posicion + 10]
                print(f"Error: Token no reconocido en posición {self.posicion}: '{error_token}'")
                print(f"Código fuente actual: '{self.codigo_fuente}'")  # Muestra el código fuente completo
                print(f"Posición actual: {self.posicion}")
                raise SyntaxError(f"Token no reconocido en posición {self.posicion}")

        self.tokens.append(Token(TipoToken.EOF, None))  # Añadir token EOF al final
        return self.tokens
