from src.core.lexer import Token, TipoToken
from src.core.parser import NodoAsignacion, NodoCondicional, NodoBucleMientras, NodoFuncion, NodoLlamadaFuncion, NodoHolobit, NodoValor


class InterpretadorCobra:
    def __init__(self):
        self.variables = {}  # Diccionario para almacenar variables y sus valores

    def ejecutar_ast(self, ast):
        resultado = None
        for nodo in ast:
            resultado = self.ejecutar_nodo(nodo)
        return resultado

    def ejecutar_nodo(self, nodo):
        if isinstance(nodo, NodoAsignacion):
            self.ejecutar_asignacion(nodo)
        elif isinstance(nodo, NodoCondicional):
            return self.ejecutar_condicional(nodo)
        elif isinstance(nodo, NodoBucleMientras):
            return self.ejecutar_mientras(nodo)
        elif isinstance(nodo, NodoFuncion):
            self.ejecutar_funcion(nodo)
        elif isinstance(nodo, NodoLlamadaFuncion):
            return self.ejecutar_llamada_funcion(nodo)
        elif isinstance(nodo, NodoHolobit):
            return self.ejecutar_holobit(nodo)
        elif isinstance(nodo, NodoValor):
            return nodo.valor  # Retorna el valor directo de NodoValor
        else:
            raise ValueError(f"Nodo no soportado: {type(nodo)}")

    def ejecutar_asignacion(self, nodo):
        # Resuelve el valor de la expresión en el nodo
        valor = self.evaluar_expresion(nodo.expresion)
        # Almacena el valor en el diccionario de variables
        self.variables[nodo.variable] = valor

    def evaluar_expresion(self, expresion):
        if isinstance(expresion, NodoValor):
            return expresion.valor  # Obtiene el valor directo si es un NodoValor
        elif isinstance(expresion, Token) and expresion.tipo in {TipoToken.ENTERO, TipoToken.FLOTANTE, TipoToken.CADENA, TipoToken.BOOLEANO}:
            return expresion.valor  # Si es un token de tipo literal, devuelve su valor
        elif isinstance(expresion, NodoAsignacion):
            self.ejecutar_asignacion(expresion)  # Resuelve asignaciones anidadas, si existieran
        else:
            raise ValueError(f"Expresión no soportada: {expresion}")

    def ejecutar_condicional(self, nodo):
        # Ejecuta el bloque de código dentro del condicional si la condición es verdadera
        if eval(nodo.condicion, {}, self.variables):  # eval simplificado para condiciones básicas
            for instruccion in nodo.cuerpo_si:
                self.ejecutar_nodo(instruccion)
        elif nodo.cuerpo_sino:
            for instruccion in nodo.cuerpo_sino:
                self.ejecutar_nodo(instruccion)

    def ejecutar_mientras(self, nodo):
        # Ejecuta el bucle mientras la condición sea verdadera
        while eval(nodo.condicion, {}, self.variables):
            for instruccion in nodo.cuerpo:
                self.ejecutar_nodo(instruccion)

    def ejecutar_funcion(self, nodo):
        # Almacena las funciones definidas por el usuario en el diccionario `variables`
        self.variables[nodo.nombre] = nodo

    def ejecutar_llamada_funcion(self, nodo):
        if nodo.nombre == "imprimir":
            for arg in nodo.argumentos:
                if isinstance(arg, NodoValor):
                    valor = arg.valor
                    if isinstance(valor, str):
                        print(valor.strip('"'))  # Imprime cadenas sin comillas
                    else:
                        print(valor)  # Imprime enteros, flotantes directamente
                elif isinstance(arg, Token) and arg.tipo == TipoToken.IDENTIFICADOR:
                    valor = self.variables.get(arg.valor, f"Variable '{arg.valor}' no definida")
                    print(valor)
                else:
                    print(f"Error: tipo de argumento no soportado para 'imprimir': {arg}")
        else:
            print(f"Función '{nodo.nombre}' no implementada")

    def ejecutar_holobit(self, nodo):
        print(f"Simulando holobit: {nodo.nombre}")
