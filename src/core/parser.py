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
        self.variable = variable  # Nombre de la variable
        self.expresion = expresion  # Expresión asignada


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

    def __repr__(self):
        return f"NodoBucleMientras"



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

    # Implementación del método token_actual() en el Parser
    def token_actual(self):
        if self.posicion < len(self.tokens):
            token = self.tokens[self.posicion]
            print(f"Token actual: {token}")  # Para depuración
            return token
        raise Exception("No hay más tokens")

    def token_siguiente(self):
        """Devuelve el siguiente token en la lista de tokens."""
        if self.posicion + 1 < len(self.tokens):
            return self.tokens[self.posicion + 1]
        return None  # Retorna None si no hay más tokens

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
        token_actual = self.token_actual()
        if token_actual.tipo == TipoToken.VAR:  # Si es una nueva declaración de variable
            self.comer(TipoToken.VAR)
        identificador = self.token_actual()
        self.comer(TipoToken.IDENTIFICADOR)  # Consumir el identificador de la variable
        self.comer(TipoToken.ASIGNAR)  # Consumir el '='
        valor = self.expresion()  # Obtener la expresión del valor
        return NodoAsignacion(identificador, valor)  # Retornar el nodo de asignación

    def declaracion(self):
        token = self.token_actual()
        print(f"Token en declaracion: {token}")  # Mensaje de depuración

        try:
            if token.tipo == TipoToken.VAR:
                return self.declaracion_asignacion()  # Manejo de asignaciones
            elif token.tipo == TipoToken.HOLOBIT:
                return self.declaracion_holobit()  # Manejo de holobits
            elif token.tipo == TipoToken.SI:
                return self.declaracion_condicional()  # Manejo de condicionales
            elif token.tipo == TipoToken.MIENTRAS:
                return self.declaracion_mientras()  # Manejo de bucles "mientras"
            elif token.tipo == TipoToken.FUNC:
                return self.declaracion_funcion()  # Manejo de funciones
            elif token.tipo == TipoToken.IDENTIFICADOR:
                print(f"Identificador encontrado: {token.valor}")  # Depuración
                siguiente_token = self.token_siguiente()  # Obtener el siguiente token de manera segura

                if siguiente_token and siguiente_token.tipo == TipoToken.LPAREN:
                    return self.llamada_funcion()  # Manejar la llamada a función
                elif siguiente_token and siguiente_token.tipo == TipoToken.ASIGNAR:
                    return self.declaracion_asignacion()  # Manejo de asignaciones
                else:
                    self.avanzar()  # Avanzar para evitar un bucle infinito
                    return NodoValor(token.valor)  # Retornar el nodo de valor si no es una asignación ni una llamada
            else:
                raise SyntaxError(f"Token inesperado: {token.tipo}")
        except Exception as e:
            print(f"Error en la declaración: {e}")
            raise  # Relanzar la excepción si es necesario

    def declaracion_mientras(self):
        self.comer(TipoToken.MIENTRAS)  # Consumir el token 'mientras'
        condicion = self.expresion()  # Obtener la expresión condicional del bucle
        self.comer(TipoToken.DOSPUNTOS)  # Consumir los dos puntos ':'

        # Procesar el cuerpo del bucle
        cuerpo = []
        while self.token_actual().tipo != TipoToken.EOF and self.token_actual().tipo != TipoToken.FIN:
            cuerpo.append(self.declaracion())  # Procesar cada declaración en el bloque del bucle

        return NodoBucleMientras(condicion, cuerpo)  # Crear el nodo 'mientras'

    def declaracion_variable(self):
        self.comer(TipoToken.VAR)
        nombre_variable = self.token_actual().valor
        self.comer(TipoToken.IDENTIFICADOR)
        self.comer(TipoToken.ASIGNAR)
        expresion = self.expresion()
        return NodoAsignacion(nombre_variable, expresion)

    def declaracion_holobit(self):
        self.comer(TipoToken.HOLOBIT)  # Consumir el token 'holobit'
        self.comer(TipoToken.LPAREN)  # Consumir el token '('
        valores = []
        self.comer(TipoToken.LBRACKET)  # Consumir el token '['

        while self.token_actual().tipo != TipoToken.RBRACKET:
            # Asegúrate de que los valores sean de tipo flotante o compatible
            if self.token_actual().tipo in [TipoToken.FLOTANTE, TipoToken.ENTERO]:
                valores.append(self.expresion())  # Procesar y añadir el valor
            else:
                raise SyntaxError(f"Tipo de valor inesperado para holobit: {self.token_actual().tipo}")

            if self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)  # Consumir la coma para el siguiente valor

        self.comer(TipoToken.RBRACKET)  # Consumir el token ']'
        self.comer(TipoToken.RPAREN)  # Consumir el token ')'

        return NodoHolobit(valores)  # Crear y retornar el nodo de holobit

    def declaracion_condicional(self):
        self.comer(TipoToken.SI)  # Asegúrate de que estamos en un 'si'

        condicion = self.expresion()  # Aquí deberías tener la condición

        self.comer(TipoToken.DOSPUNTOS)  # Mover al token ':'
        bloque_si = self.bloque()  # Procesar el bloque 'si'

        if self.token_actual().tipo == TipoToken.SINO:
            self.comer(TipoToken.SINO)  # Mover al token 'sino'
            self.comer(TipoToken.DOSPUNTOS)  # Mover al token ':'
            bloque_sino = self.bloque()  # Procesar el bloque 'sino'
            return NodoCondicional(condicion, bloque_si, bloque_sino)

        return NodoCondicional(condicion, bloque_si, None)  # Si no hay bloque 'sino'

    def declaracion_bucle_mientras(self):
        self.comer(TipoToken.MIENTRAS)
        condicion = self.expresion()  # Aquí esperas una expresión que sea la condición
        self.comer(TipoToken.DOSPUNTOS)

        # Manejo del bloque del bucle (puedes usar una lista para almacenar las declaraciones)
        declaraciones = []
        while self.token_actual().tipo != TipoToken.EOF:  # O el token que delimite el final del bloque
            declaraciones.append(self.declaracion())  # Procesar cada declaración en el bloque

        return NodoBucleMientras(condicion, declaraciones)  # Retorna el nodo de bucle mientras

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

    # Función dentro del Parser para manejar la llamada a funciones
    def llamada_funcion(self):
        nombre_funcion = self.token_actual().valor  # Obtener el nombre de la función
        self.comer(TipoToken.IDENTIFICADOR)  # Consumir el token de identificador
        self.comer(TipoToken.LPAREN)  # Asegúrate de que hay un paréntesis de apertura

        argumentos = []
        while self.token_actual().tipo != TipoToken.RPAREN:
            argumentos.append(self.expresion())  # Procesar el argumento
            if self.token_actual().tipo == TipoToken.COMA:
                self.comer(TipoToken.COMA)  # Consumir la coma si hay más argumentos

        self.comer(TipoToken.RPAREN)  # Consumir el paréntesis de cierre
        return NodoLlamadaFuncion(nombre_funcion, argumentos)  # Retorna el nodo de llamada a función

    # Manejo de bloques de instrucciones
    def bloque(self):
        nodos = []
        while self.token_actual().tipo != TipoToken.EOF:
            try:
                nodos.append(self.declaracion())
            except SyntaxError as e:
                print(f"Error de sintaxis en el bloque: {e}")
                break  # Puedes decidir si quieres detener la ejecución o continuar
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
