from src.core.lexer import TipoToken


# Definición de nodos AST
class NodoAST:
    def __init__(self):
        pass

    def aceptar(self, visitante):
        """
        Método que permite que un visitante visite este nodo.
        Este patrón es útil para operaciones como evaluación, impresión o transformación del árbol.
        """
        raise NotImplementedError("Este método debe ser implementado por subclases.")


class NodoAsignacion:
    def __init__(self, variable, expresion):
        self.variable = variable  # Este debe ser el nombre de la variable
        self.expresion = expresion  # Esta es la expresión asignada


class NodoHolobit(NodoAST):
    def __init__(self, valores):
        super().__init__()
        self.valores = valores


class NodoCondicional(NodoAST):
    def __init__(self, condicion, bloque_si, bloque_sino=None):
        """
        :param condicion:
        :param bloque_si:
        :param bloque_sino:
        """
        super().__init__()
        self.condicion = condicion
        self.bloque_si = bloque_si
        self.bloque_sino = bloque_sino


class NodoBucleMientras(NodoAST):
    def __init__(self, condicion, cuerpo):
        super().__init__()
        self.condicion = condicion
        self.cuerpo = cuerpo


class NodoFuncion(NodoAST):
    def __init__(self, nombre, parametros, cuerpo):
        super().__init__()
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo


class NodoOperacionBinaria(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        super().__init__()
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha


class NodoValor(NodoAST):
    def __init__(self, valor):
        """

        :param valor:
        """
        super().__init__()
        self.valor = valor


class NodoLlamadaFuncion(NodoAST):
    def __init__(self, nombre, argumentos):
        super().__init__()
        self.nombre = nombre  # El nombre de la función
        self.argumentos = argumentos  # Lista de expresiones que representan los argumentos

    def aceptar(self, visitante):
        """
        Implementa el patrón visitante para este nodo.
        """
        return visitante.visitar_llamada_funcion(self)


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

    def comer(self, tipo):
        if self.token_actual().tipo == tipo:
            self.avanzar()
        else:
            raise SyntaxError(f"Se esperaba {tipo}, pero se encontró {self.token_actual().tipo}")

    def parsear(self):
        nodos = []
        while self.token_actual().tipo != TipoToken.EOF:
            nodos.append(self.declaracion())
        return nodos

    def declaracion_asignacion(self):
        variable = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.ASIGNAR)
        valor = self.expresion()
        return NodoAsignacion(variable, valor)

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
        elif token.tipo == TipoToken.IDENTIFICADOR:
            # Manejo de asignaciones o llamadas a funciones
            if self.tokens[self.posicion + 1].tipo == TipoToken.ASIGNAR:
                return self.declaracion_asignacion()
            elif self.tokens[self.posicion + 1].tipo == TipoToken.LPAREN:
                return self.llamada_funcion()
            else:
                valor = self.token_actual().valor
                self.avanzar()
                return NodoValor(valor)
        else:
            raise SyntaxError(f"Token inesperado {token.tipo}")

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
        self.comer(TipoToken.SI)  # Consume 'si'
        condicion = self.expresion()  # Procesa la condición

        self.comer(TipoToken.DOSPUNTOS)  # Consume ':'
        bloque_si = self.bloque()  # Procesa el bloque si

        # Aquí puedes manejar el 'sino'
        bloque_sino = None
        if self.token_actual().tipo == TipoToken.SINO:
            self.comer(TipoToken.SINO)  # Consume 'sino'
            self.comer(TipoToken.DOSPUNTOS)  # Consume ':'
            bloque_sino = self.bloque()  # Procesa el bloque sino

        return NodoCondicional(condicion, bloque_si, bloque_sino)  # Retorna el nodo condicional

    def declaracion_mientras(self):
        self.comer(TipoToken.MIENTRAS)
        condicion = self.expresion()
        self.comer(TipoToken.DOSPUNTOS)
        cuerpo = self.bloque()
        return NodoBucleMientras(condicion, cuerpo)

    def declaracion_funcion(self):
        self.comer(TipoToken.FUNC)  # 'func'
        nombre = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)  # Nombre de la función
        self.comer(TipoToken.LPAREN)  # '('
        parametros = self.lista_parametros()
        self.comer(TipoToken.RPAREN)  # ')'
        self.comer(TipoToken.DOSPUNTOS)  # ':'
        cuerpo = self.bloque()  # Aquí se procesan las declaraciones dentro de la función

        return NodoFuncion(nombre, parametros, cuerpo)

    def llamada_funcion(self):
        nombre = self.token_actual().valor  # Obtener el nombre de la función
        self.comer(TipoToken.IDENTIFICADOR)  # Consumir el nombre de la función
        self.comer(TipoToken.LPAREN)  # Consumir '('

        argumentos = []
        if self.token_actual().tipo != TipoToken.RPAREN:
            argumentos.append(self.expresion())  # Procesar los argumentos de la función
            while self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)
                argumentos.append(self.expresion())

        self.comer(TipoToken.RPAREN)  # Consumir ')'
        return NodoLlamadaFuncion(nombre, argumentos)

    # Manejo de bloques de instrucciones
    def bloque(self):
        nodos = []
        while self.token_actual().tipo not in [TipoToken.EOF, TipoToken.SINO]:
            nodos.append(self.declaracion())
        return nodos

    # Manejo de expresiones
    def expresion(self):
        izquierda = self.termino()

        # Aceptar operadores relacionales en expresiones
        while self.token_actual().tipo in [TipoToken.SUMA, TipoToken.RESTA, TipoToken.MAYORQUE]:
            operador = self.token_actual()
            self.avanzar()
            derecha = self.termino()
            izquierda = NodoOperacionBinaria(izquierda, operador, derecha)

        return izquierda

    def termino(self):
        token = self.token_actual()

        # Manejo de números negativos
        if token.tipo == TipoToken.RESTA:
            self.comer(TipoToken.RESTA)
            numero = self.token_actual()
            if numero.tipo in [TipoToken.ENTERO, TipoToken.FLOTANTE]:
                valor = -numero.valor  # Aplicar el signo negativo
                self.avanzar()
                return NodoValor(valor)
            else:
                raise SyntaxError(f"Se esperaba un número después del signo '-', pero se encontró {numero.tipo}")

        # Manejo de enteros y flotantes
        elif token.tipo in [TipoToken.ENTERO, TipoToken.FLOTANTE]:
            valor = token.valor
            self.avanzar()
            return NodoValor(valor)

        # Manejo de cadenas
        elif token.tipo == TipoToken.CADENA:
            valor = token.valor
            self.avanzar()
            return NodoValor(valor)

        # Manejo de identificadores
        elif token.tipo == TipoToken.IDENTIFICADOR:
            valor = token.valor
            self.avanzar()
            return NodoValor(valor)

        # Manejo de holobits
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
