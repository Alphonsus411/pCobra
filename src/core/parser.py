import logging
import json
from src.core.lexer import TipoToken


# Definición de nodos AST
class NodoAST:
    def __init__(self):
        pass

    def aceptar(self, visitante):
        raise NotImplementedError("Este método debe ser implementado por subclases.")


class NodoAsignacion(NodoAST):
    def __init__(self, variable, expresion):
        super().__init__()
        self.variable = variable
        self.expresion = expresion


class NodoHolobit(NodoAST):
    def __init__(self, valores):
        super().__init__()
        self.valores = valores


class NodoCondicional(NodoAST):
    def __init__(self, condicion, bloque_si, bloque_sino=None):
        super().__init__()
        self.condicion = condicion
        self.bloque_si = bloque_si
        self.bloque_sino = bloque_sino


class NodoBucleMientras(NodoAST):
    def __init__(self, condicion, cuerpo):
        super().__init__()
        self.condicion = condicion
        self.cuerpo = cuerpo


class NodoFor(NodoAST):
    def __init__(self, variable, iterable, cuerpo):
        super().__init__()
        self.variable = variable
        self.iterable = iterable
        self.cuerpo = cuerpo


class NodoLista(NodoAST):
    def __init__(self, elementos):
        super().__init__()
        self.elementos = elementos


class NodoDiccionario(NodoAST):
    def __init__(self, elementos):
        super().__init__()
        self.elementos = elementos


class NodoFuncion(NodoAST):
    def __init__(self, nombre, parametros, cuerpo):
        super().__init__()
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo


class NodoClase(NodoAST):
    def __init__(self, nombre, metodos):
        super().__init__()
        self.nombre = nombre
        self.metodos = metodos


class NodoMetodo(NodoAST):
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
        super().__init__()
        self.valor = valor


class NodoLlamadaFuncion(NodoAST):
    def __init__(self, nombre, argumentos):
        super().__init__()
        self.nombre = nombre
        self.argumentos = argumentos


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.indentacion_actual = 0

    def token_actual(self):
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        raise Exception("No hay más tokens")

    def token_siguiente(self):
        if self.posicion + 1 < len(self.tokens):
            return self.tokens[self.posicion + 1]
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

    def declaracion(self):
        token = self.token_actual()
        try:
            if token.tipo == TipoToken.VAR:
                return self.declaracion_asignacion()
            elif token.tipo == TipoToken.HOLOBIT:
                return self.declaracion_holobit()
            elif token.tipo == TipoToken.SI:
                return self.declaracion_condicional()
            elif token.tipo == TipoToken.MIENTRAS:
                return self.declaracion_mientras()
            elif token.tipo == TipoToken.FUNC:
                return self.declaracion_funcion()
            elif token.tipo == TipoToken.IDENTIFICADOR:
                siguiente_token = self.token_siguiente()
                if siguiente_token and siguiente_token.tipo == TipoToken.LPAREN:
                    return self.llamada_funcion()
                elif siguiente_token and siguiente_token.tipo == TipoToken.ASIGNAR:
                    return self.declaracion_asignacion()
                else:
                    self.avanzar()
                    return NodoValor(token.valor)
            else:
                raise SyntaxError(f"Token inesperado: {token.tipo}")
        except Exception as e:
            logging.debug(f"Error en la declaración: {e}")
            raise

    def declaracion_asignacion(self):
        self.comer(TipoToken.VAR)
        identificador = self.token_actual()
        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.ASIGNAR)
        valor = self.expresion()
        return NodoAsignacion(identificador, valor)

    def declaracion_mientras(self):
        self.comer(TipoToken.MIENTRAS)
        condicion = self.expresion()
        self.comer(TipoToken.DOSPUNTOS)
        cuerpo = self.bloque()
        return NodoBucleMientras(condicion, cuerpo)

    def declaracion_holobit(self):
        self.comer(TipoToken.HOLOBIT)
        self.comer(TipoToken.LPAREN)
        valores = []
        self.comer(TipoToken.LBRACKET)
        while self.token_actual().tipo != TipoToken.RBRACKET:
            if self.token_actual().tipo in [TipoToken.FLOTANTE, TipoToken.ENTERO]:
                valores.append(self.expresion())
            if self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)
        self.comer(TipoToken.RBRACKET)
        self.comer(TipoToken.RPAREN)
        return NodoHolobit(valores)

    def declaracion_condicional(self):
        self.comer(TipoToken.SI)
        condicion = self.expresion()
        self.comer(TipoToken.DOSPUNTOS)
        bloque_si = self.bloque()
        bloque_sino = None
        if self.token_actual().tipo == TipoToken.SINO:
            self.comer(TipoToken.SINO)
            self.comer(TipoToken.DOSPUNTOS)
            bloque_sino = self.bloque()
        return NodoCondicional(condicion, bloque_si, bloque_sino)

    def declaracion_funcion(self):
        self.comer(TipoToken.FUNC)
        nombre = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.LPAREN)
        parametros = self.lista_parametros()
        self.comer(TipoToken.RPAREN)
        self.comer(TipoToken.DOSPUNTOS)
        cuerpo = self.bloque()
        return NodoFuncion(nombre, parametros, cuerpo)

    def llamada_funcion(self):
        nombre_funcion = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.LPAREN)
        argumentos = []
        while self.token_actual().tipo != TipoToken.RPAREN:
            argumentos.append(self.expresion())
            if self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)
        self.comer(TipoToken.RPAREN)
        return NodoLlamadaFuncion(nombre_funcion, argumentos)

    def bloque(self):
        nodos = []
        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            try:
                nodos.append(self.declaracion())
            except SyntaxError as e:
                logging.debug(f"Error de sintaxis en el bloque: {e}")
                break
        return nodos

    def expresion(self):
        izquierda = self.termino()
        while self.token_actual().tipo in [TipoToken.SUMA, TipoToken.RESTA, TipoToken.MAYORQUE]:
            operador = self.token_actual()
            self.avanzar()
            derecha = self.termino()
            izquierda = NodoOperacionBinaria(izquierda, operador, derecha)
        return izquierda

    def termino(self):
        token = self.token_actual()
        if token.tipo in [TipoToken.ENTERO, TipoToken.FLOTANTE]:
            self.avanzar()
            return NodoValor(token.valor)
        elif token.tipo == TipoToken.IDENTIFICADOR:
            return NodoValor(token.valor)
        else:
            raise SyntaxError(f"Token inesperado en término: {token.tipo}")

    def lista_parametros(self):
        parametros = []
        while self.token_actual().tipo == TipoToken.IDENTIFICADOR:
            nombre_parametro = self.token_actual().valor
            if nombre_parametro in ["si", "mientras", "func", "fin"]:
                raise SyntaxError(f"El nombre del parámetro '{nombre_parametro}' es reservado.")
            if nombre_parametro in parametros:
                raise SyntaxError(f"El parámetro '{nombre_parametro}' ya está definido.")
            parametros.append(nombre_parametro)
            self.comer(TipoToken.IDENTIFICADOR)
            if self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)
        return parametros

    def ast_to_json(self, nodo):
        """Exporta el AST a un formato JSON para depuración o visualización."""
        return json.dumps(nodo, default=lambda o: o.__dict__, indent=4)
