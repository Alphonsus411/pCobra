from src.core.lexer import TipoToken


# Definición de nodos AST
class NodoAST:
    pass


class NodoAsignacion(NodoAST):
    def __init__(self, variable, expresion):
        self.variable = variable
        self.expresion = expresion


class NodoHolobit(NodoAST):
    def __init__(self, valores):
        self.valores = valores


class NodoCondicional(NodoAST):
    def __init__(self, condicion, bloque_si, bloque_sino=None):
        self.condicion = condicion
        self.bloque_si = bloque_si
        self.bloque_sino = bloque_sino


class NodoBucleMientras(NodoAST):
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo


class NodoFuncion(NodoAST):
    def __init__(self, nombre, parametros, cuerpo):
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo


class NodoOperacionBinaria(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha


class NodoValor(NodoAST):
    def __init__(self, valor):
        self.valor = valor


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0

    def token_actual(self):
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        return None

    def avanzar(self):
        self.posicion += 1
        if self.posicion < len(self.tokens):
            print(f"Avanzando al siguiente token: {self.token_actual()}")

    def comer(self, tipo):
        if self.token_actual().tipo == tipo:
            print(f"Comiendo token: {self.token_actual()}")
            self.avanzar()
        else:
            raise SyntaxError(f"Se esperaba {tipo}, pero se encontró {self.token_actual().tipo}")

    def parsear(self):
        nodos = []
        while self.token_actual().tipo != TipoToken.EOF:
            nodos.append(self.declaracion())
        return nodos

    def declaracion(self):
        token = self.token_actual()

        if token.tipo == TipoToken.VAR:
            return self.declaracion_variable()

        elif token.tipo == TipoToken.HOLOBIT:
            return self.declaracion_holobit()

        elif token.tipo == TipoToken.SI:
            return self.declaracion_condicional()

        elif token.tipo == TipoToken.MIENTRAS:
            return self.declaracion_mientras()

        elif token.tipo == TipoToken.FUNC:
            return self.declaracion_funcion()

        else:
            raise SyntaxError(f"Token inesperado {token.tipo}")

    # Declaraciones
    def declaracion_variable(self):
        self.comer(TipoToken.VAR)
        nombre_variable = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.ASIGNAR)
        expresion = self.expresion()
        return NodoAsignacion(nombre_variable, expresion)

    def declaracion_holobit(self):
        self.comer(TipoToken.HOLOBIT)
        self.comer(TipoToken.LPAREN)
        valores = []
        self.comer(TipoToken.LBRACKET)

        while self.token_actual().tipo != TipoToken.RBRACKET:
            valores.append(self.expresion())
            if self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)

        self.comer(TipoToken.RBRACKET)
        self.comer(TipoToken.RPAREN)
        return NodoHolobit(valores)

    def declaracion_condicional(self):
        self.comer(TipoToken.SI)
        condicion = self.expresion()
        self.comer(TipoToken.DOSPUNTOS)  # Cambiado a TipoToken FLECHA
        bloque_si = self.bloque()

        bloque_sino = None
        if self.token_actual().tipo == TipoToken.SINO:
            self.comer(TipoToken.SINO)
            self.comer(TipoToken.DOSPUNTOS)
            bloque_sino = self.bloque()

        return NodoCondicional(condicion, bloque_si, bloque_sino)

    def declaracion_mientras(self):
        self.comer(TipoToken.MIENTRAS)
        condicion = self.expresion()
        self.comer(TipoToken.DOSPUNTOS)  # Cambiado a TipoToken
        cuerpo = self.bloque()
        return NodoBucleMientras(condicion, cuerpo)

    def declaracion_funcion(self):
        self.comer(TipoToken.FUNC)
        nombre_funcion = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.LPAREN)
        parametros = self.lista_parametros()
        self.comer(TipoToken.RPAREN)
        self.comer(TipoToken.DOSPUNTOS)  # Cambiado a TipoToken
        cuerpo = self.bloque()
        return NodoFuncion(nombre_funcion, parametros, cuerpo)

    # Bloque de instrucciones
    def bloque(self):
        nodos = []
        while self.token_actual().tipo not in [TipoToken.SINO, TipoToken.EOF]:
            nodos.append(self.declaracion())
        return nodos

    # Expresiones
    def expresion(self):
        izquierda = self.termino()

        while self.token_actual().tipo in [TipoToken.SUMA, TipoToken.RESTA]:
            operador = self.token_actual()
            self.avanzar()
            derecha = self.termino()
            izquierda = NodoOperacionBinaria(izquierda, operador, derecha)

        return izquierda

    def termino(self):
        token = self.token_actual()

        if token.tipo in [TipoToken.ENTERO, TipoToken.FLOTANTE]:
            valor = token.valor
            self.avanzar()
            return NodoValor(valor)

        elif token.tipo == TipoToken.IDENTIFICADOR:
            valor = token.valor
            self.avanzar()
            return NodoValor(valor)

        elif token.tipo == TipoToken.HOLOBIT:
            return self.declaracion_holobit()

        else:
            raise SyntaxError(f"Token inesperado {token.tipo}")

    def lista_parametros(self):
        parametros = []
        while self.token_actual().tipo != TipoToken.RPAREN:
            parametros.append(self.token_actual().valor)
            self.avanzar()
            if self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)
        return parametros
