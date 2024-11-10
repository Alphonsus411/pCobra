import re


class TipoToken:
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
    FIN = 'FIN'
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

        prev_pos = -1
        same_pos_count = 0
        error_tokens = []

        while self.posicion < len(self.codigo_fuente):
            matched = False
            for tipo, patron in especificacion_tokens:
                regex = re.compile(patron)
                coincidencia = regex.match(self.codigo_fuente[self.posicion:])
                if coincidencia:
                    if tipo:
                        valor = coincidencia.group(0)
                        print(f"Token identificado: {tipo}, valor: '{valor}', posición: {self.posicion}")

                        if tipo == TipoToken.FLOTANTE:
                            valor = float(valor)
                        elif tipo == TipoToken.ENTERO:
                            valor = int(valor)
                        self.tokens.append(Token(tipo, valor))

                    self.posicion += len(coincidencia.group(0))
                    matched = True
                    break

            if not matched:
                # Si no coincide con ningún patrón, capturamos el error
                try:
                    error_token = self.codigo_fuente[self.posicion:self.posicion + 10]
                    print(f"Error: Token no reconocido en posición {self.posicion}: '{error_token}'")
                    error_tokens.append(error_token)  # Almacena el token no reconocido
                    self.posicion += 1  # Avanza para evitar quedarse en el mismo carácter
                except Exception as e:
                    print(f"Excepción al procesar el token en posición {self.posicion}: {e}")

            if self.posicion == prev_pos:
                same_pos_count += 1
                if same_pos_count > 5:
                    print(f"Bucle infinito detectado en posición {self.posicion}.")
                    raise RuntimeError("Bucle infinito detectado en el lexer.")
            else:
                same_pos_count = 0

            prev_pos = self.posicion

        if error_tokens:
            print(f"Tokens no reconocidos encontrados: {error_tokens}")

        return self.tokens
