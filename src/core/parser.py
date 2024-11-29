import logging
import json
from src.core.lexer import TipoToken

logging.basicConfig(level=logging.DEBUG)


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


class NodoIdentificador:
    """
    Representa un nodo en el AST para un identificador.
    """

    def __init__(self, nombre):
        """
        Inicializa el nodo con el nombre del identificador.

        :param nombre: Nombre del identificador (cadena de texto).
        """
        self.nombre = nombre

    def __repr__(self):
        return f'NodoIdentificador({self.nombre})'

    def evaluar(self, contexto):
        """
        Evalúa el identificador en el contexto actual.

        :param contexto: Un diccionario u objeto que representa las variables actuales.
        :return: El valor asociado al identificador en el contexto.
        :raises NameError: Si el identificador no existe en el contexto.
        """
        if self.nombre in contexto:
            return contexto[self.nombre]
        else:
            raise NameError(f"Identificador no definido: '{self.nombre}'")


class NodoLlamadaFuncion(NodoAST):
    def __init__(self, nombre, argumentos):
        super().__init__()
        self.nombre = nombre
        self.argumentos = argumentos


class NodoRetorno(NodoAST):
    def __init__(self, expresion):
        super().__init__()
        self.expresion = expresion

    def __repr__(self):
        return f"NodoRetorno(expresion={self.expresion})"


class NodoMientras:
    """Representa un nodo de bucle 'mientras' en el AST."""

    def __init__(self, condicion, cuerpo):
        """
        Inicializa el nodo de bucle mientras.

        :param condicion: Nodo que representa la condición del bucle.
        :param cuerpo: Lista de nodos que representan el cuerpo del bucle.
        """
        self.condicion = condicion
        self.cuerpo = cuerpo

    def __repr__(self):
        return f"NodoMientras(condicion={self.condicion}, cuerpo={self.cuerpo})"


class NodoImprimir(NodoAST):
    """Nodo para representar una instrucción de impresión."""

    def __init__(self, expresion):
        super().__init__()
        self.expresion = expresion

    def __repr__(self):
        return f"NodoImprimir(expresion={self.expresion})"


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
        """Procesa una declaración, ya sea una asignación, condición, bucle, función o expresión."""
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
            elif token.tipo == TipoToken.IMPRIMIR:  # Soporte para `imprimir`
                return self.declaracion_imprimir()
            elif token.tipo in [TipoToken.IDENTIFICADOR, TipoToken.ENTERO, TipoToken.FLOTANTE]:
                siguiente_token = self.token_siguiente()
                if siguiente_token and siguiente_token.tipo == TipoToken.LPAREN:
                    return self.llamada_funcion()
                elif siguiente_token and siguiente_token.tipo == TipoToken.ASIGNAR:
                    return self.declaracion_asignacion()
                else:
                    return self.expresion()  # Procesa como una expresión
            else:
                raise SyntaxError(f"Token inesperado: {token.tipo}")
        except Exception as e:
            logging.debug(f"Error en la declaración: {e}")
            raise

    def termino(self):
        """Parsea un término (literal, identificador, o expresión entre paréntesis)."""
        token = self.token_actual()
        if token.tipo in [TipoToken.ENTERO, TipoToken.CADENA, TipoToken.FLOTANTE, TipoToken.IDENTIFICADOR]:
            self.avanzar()
            return NodoValor(token.valor)
        elif token.tipo == TipoToken.LPAREN:
            self.comer(TipoToken.LPAREN)
            nodo = self.expresion()
            self.comer(TipoToken.RPAREN)
            return nodo
        else:
            raise SyntaxError(f"Token inesperado en término: {token.tipo}")

    def expresion(self):
        """Parsea una expresión."""
        izquierda = self.termino()
        while self.token_actual().tipo in [TipoToken.SUMA, TipoToken.RESTA, TipoToken.MULTIPLICAR, TipoToken.DIVIDIR]:
            operador = self.token_actual()
            self.avanzar()
            derecha = self.termino()
            izquierda = NodoOperacionBinaria(izquierda, operador, derecha)
        return izquierda

    def declaracion_asignacion(self):
        if self.token_actual().tipo == TipoToken.VAR:
            self.comer(TipoToken.VAR)  # Consume el token 'var' si está presente
        identificador = self.token_actual()
        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.ASIGNAR)
        valor = self.expresion()
        return NodoAsignacion(identificador, valor)

    def declaracion_mientras(self):
        """Parsea un bucle mientras."""
        self.comer(TipoToken.MIENTRAS)
        condicion = self.expresion()
        logging.debug(f"Condición del bucle mientras: {condicion}")

        # Verificar ':' después de la condición
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError("Se esperaba ':' después de la condición del bucle 'mientras'")
        self.comer(TipoToken.DOSPUNTOS)

        cuerpo = []
        while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            try:
                cuerpo.append(self.declaracion())
            except SyntaxError as e:
                logging.error(f"Error en el cuerpo del bucle 'mientras': {e}")
                self.avanzar()  # Avanza para evitar bloqueo

        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError("Se esperaba 'fin' para cerrar el bucle 'mientras'")
        self.comer(TipoToken.FIN)

        logging.debug(f"Cuerpo del bucle mientras: {cuerpo}")
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
        """Parsea un bloque condicional."""
        self.comer(TipoToken.SI)
        condicion = self.expresion()
        logging.debug(f"Condición del condicional: {condicion}")

        # Verificar ':' después de la condición
        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError("Se esperaba ':' después de la condición del 'si'")
        self.comer(TipoToken.DOSPUNTOS)

        bloque_si = []
        while self.token_actual().tipo not in [TipoToken.SINO, TipoToken.FIN, TipoToken.EOF]:
            try:
                bloque_si.append(self.declaracion())
            except SyntaxError as e:
                logging.error(f"Error en el bloque 'si': {e}")
                self.avanzar()  # Evitar bloqueo en caso de error

        bloque_sino = []
        if self.token_actual().tipo == TipoToken.SINO:
            self.comer(TipoToken.SINO)
            if self.token_actual().tipo != TipoToken.DOSPUNTOS:
                raise SyntaxError("Se esperaba ':' después del 'sino'")
            self.comer(TipoToken.DOSPUNTOS)
            while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
                try:
                    bloque_sino.append(self.declaracion())
                except SyntaxError as e:
                    logging.error(f"Error en el bloque 'sino': {e}")
                    self.avanzar()

        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError("Se esperaba 'fin' para cerrar el bloque condicional")
        self.comer(TipoToken.FIN)

        logging.debug(f"Bloque si: {bloque_si}, Bloque sino: {bloque_sino}")
        return NodoCondicional(condicion, bloque_si, bloque_sino)

    def declaracion_funcion(self):
        """Parsea una declaración de función."""
        self.comer(TipoToken.FUNC)
        nombre = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.LPAREN)
        parametros = self.lista_parametros()
        self.comer(TipoToken.RPAREN)

        if self.token_actual().tipo != TipoToken.DOSPUNTOS:
            raise SyntaxError("Se esperaba ':' después de la declaración de la función")
        self.comer(TipoToken.DOSPUNTOS)

        cuerpo = []
        if self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
            max_iteraciones = 1000  # Límite para evitar bucles infinitos
            iteraciones = 0

            while self.token_actual().tipo not in [TipoToken.FIN, TipoToken.EOF]:
                iteraciones += 1
                if iteraciones > max_iteraciones:
                    raise RuntimeError("Bucle infinito detectado en declaracion_funcion")

                try:
                    if self.token_actual().tipo == TipoToken.RETORNO:
                        self.comer(TipoToken.RETORNO)
                        expresion = self.expresion()
                        cuerpo.append(NodoRetorno(expresion))
                    else:
                        cuerpo.append(self.declaracion())
                except SyntaxError as e:
                    logging.error(f"Error en el cuerpo de la función '{nombre}': {e}")
                    self.avanzar()

        if self.token_actual().tipo != TipoToken.FIN:
            raise SyntaxError(f"Se esperaba 'fin' para cerrar la función '{nombre}'")
        self.comer(TipoToken.FIN)

        logging.debug(f"Función '{nombre}' parseada con cuerpo: {cuerpo}")
        return NodoFuncion(nombre, parametros, cuerpo)

    def expresion(self):
        izquierda = self.termino()
        while self.token_actual().tipo in [TipoToken.SUMA, TipoToken.RESTA, TipoToken.MAYORQUE]:
            operador = self.token_actual()
            self.avanzar()
            derecha = self.termino()
            izquierda = NodoOperacionBinaria(izquierda, operador, derecha)
        return izquierda

    def termino(self):
        """Procesa términos como literales, identificadores y llamados a funciones."""
        token = self.token_actual()
        if token.tipo == TipoToken.ENTERO:
            self.comer(TipoToken.ENTERO)
            return NodoValor(token.valor)
        elif token.tipo == TipoToken.FLOTANTE:
            self.comer(TipoToken.FLOTANTE)
            return NodoValor(token.valor)
        elif token.tipo == TipoToken.CADENA:
            self.comer(TipoToken.CADENA)
            return NodoValor(token.valor)
        elif token.tipo == TipoToken.IDENTIFICADOR:
            siguiente_token = self.token_siguiente()
            if siguiente_token and siguiente_token.tipo == TipoToken.LPAREN:
                return self.llamada_funcion()
            self.comer(TipoToken.IDENTIFICADOR)
            return NodoIdentificador(token.valor)
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


