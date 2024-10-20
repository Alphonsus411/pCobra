import re


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
    SUMA = 'SUMA'
    RESTA = 'RESTA'
    MULT = 'MULT'
    DIV = 'DIV'
    ASIGNAR = 'ASIGNAR'
    DOSPUNTOS = 'DOSPUNTOS'
    MAYORQUE = 'MAYORQUE'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LLLAVE = 'LLAVE'
    RLLAVE = 'RLLAVE'
    COMA = 'COMA'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    EOF = 'EOF'
    FIN = 'FIN'


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

    def analizar_token(self):
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
            (TipoToken.FLOTANTE, r'\d+\.\d+'),  # Flotantes sin el signo negativo
            (TipoToken.ENTERO, r'\d+'),  # Enteros sin el signo negativo
            (TipoToken.CADENA, r"'[^']*'|\"[^\"]*\""),  # Cadenas entre comillas simples o dobles
            (TipoToken.BOOLEANO, r'\b(verdadero|falso)\b'),
            (TipoToken.IDENTIFICADOR, r'[A-Za-z_][A-Za-z0-9_]*'),
            (TipoToken.ASIGNAR, r'='),
            (TipoToken.DOSPUNTOS, r':'),  # Usamos ':' como símbolo de dos puntos
            (TipoToken.SUMA, r'\+'),
            (TipoToken.RESTA, r'-'),  # El signo menos se trata por separado
            (TipoToken.MULT, r'\*'),
            (TipoToken.DIV, r'/'),
            (TipoToken.MAYORQUE, r'>'),  # Asegurarse que MAYORQUE esté después de DOSPUNTOS
            (TipoToken.LPAREN, r'\('),
            (TipoToken.RPAREN, r'\)'),
            (TipoToken.LBRACKET, r'\['),  # Corchetes de apertura
            (TipoToken.RBRACKET, r'\]'),  # Corchetes de cierre
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
                        print(f"Token encontrado: {valor} en posición {self.posicion}")
                        self.tokens.append(Token(tipo, valor))
                    self.posicion += len(coincidencia.group(0))
                    matched = True
                    break

            if not matched:
                print(
                    f"Error: Token no reconocido en posición {self.posicion}: {self.codigo_fuente[self.posicion:self.posicion + 10]}")
                raise SyntaxError(f"Token no reconocido en posición {self.posicion}")

        self.tokens.append(Token(TipoToken.EOF, None))  # Añadir token EOF al final
        return self.tokens
