from src.core.lexer import Token, TipoToken
from src.core.parser import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoValor,
    NodoImprimir,
    NodoRetorno,
)


class InterpretadorCobra:
    """Interpreta y ejecuta nodos del lenguaje Cobra."""
    def __init__(self):
        self.variables = {}  # Diccionario para almacenar variables y sus valores

    def ejecutar_ast(self, ast):
        for nodo in ast:
            resultado = self.ejecutar_nodo(nodo)
            if resultado is not None:
                return resultado
        return None

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
        elif isinstance(nodo, NodoImprimir):
            valor = self.evaluar_expresion(nodo.expresion)
            if isinstance(valor, str):
                if (valor.startswith("\"") and valor.endswith("\"")) or (
                    valor.startswith("'") and valor.endswith("'")
                ):
                    print(valor.strip('"').strip("'"))
                elif valor in self.variables:
                    print(self.variables[valor])
                else:
                    print(f"Variable '{valor}' no definida")
            else:
                print(valor)
        elif isinstance(nodo, NodoHolobit):
            return self.ejecutar_holobit(nodo)
        elif isinstance(nodo, NodoRetorno):
            return self.evaluar_expresion(nodo.expresion)
        elif isinstance(nodo, NodoValor):
            return nodo.valor  # Retorna el valor directo de NodoValor
        else:
            raise ValueError(f"Nodo no soportado: {type(nodo)}")

    def ejecutar_asignacion(self, nodo):
        # Resuelve el valor de la expresión en el nodo
        nombre = getattr(nodo, "identificador", getattr(nodo, "variable", None))
        valor_nodo = getattr(nodo, "expresion", getattr(nodo, "valor", None))
        # Resuelve el valor de la expresión en el nodo
        valor = self.evaluar_expresion(valor_nodo)
        # Almacena el valor en el diccionario de variables
        self.variables[nombre] = valor

    def evaluar_expresion(self, expresion):
        if isinstance(expresion, NodoValor):
            return expresion.valor  # Obtiene el valor directo si es un NodoValor
        elif isinstance(expresion, Token) and expresion.tipo in {
            TipoToken.ENTERO,
            TipoToken.FLOTANTE,
            TipoToken.CADENA,
            TipoToken.BOOLEANO,
        }:
            return expresion.valor  # Si es un token de tipo literal, devuelve su valor
        elif isinstance(expresion, NodoAsignacion):
            # Resuelve asignaciones anidadas, si existieran
            self.ejecutar_asignacion(expresion)
        elif isinstance(expresion, NodoHolobit):
            return self.ejecutar_holobit(expresion)
        else:
            raise ValueError(f"Expresión no soportada: {expresion}")

    def ejecutar_condicional(self, nodo):
        """Ejecuta un bloque condicional."""
        if eval(
            nodo.condicion,
            {},
            self.variables,
        ):  # eval simplificado para condiciones básicas
            for instruccion in nodo.cuerpo_si:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado
        elif nodo.cuerpo_sino:
            for instruccion in nodo.cuerpo_sino:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado

    def ejecutar_mientras(self, nodo):
        # Ejecuta el bucle mientras la condición sea verdadera
        while eval(nodo.condicion, {}, self.variables):
            for instruccion in nodo.cuerpo:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado

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
                elif (
                    isinstance(arg, Token)
                    and arg.tipo == TipoToken.IDENTIFICADOR
                ):
                    valor = self.variables.get(
                        arg.valor,
                        f"Variable '{arg.valor}' no definida",
                    )
                    print(valor)
                else:
                    print(
                        "Error: tipo de argumento no soportado para 'imprimir': "
                        f"{arg}"
                    )
        elif nodo.nombre in self.variables and isinstance(self.variables[nodo.nombre], NodoFuncion):
            funcion = self.variables[nodo.nombre]
            if len(funcion.parametros) != len(nodo.argumentos):
                print(f"Error: se esperaban {len(funcion.parametros)} argumentos")
                return None
            contexto_anterior = self.variables.copy()
            for nombre_param, arg in zip(funcion.parametros, nodo.argumentos):
                self.variables[nombre_param] = self.evaluar_expresion(arg)
            resultado = None
            for instruccion in funcion.cuerpo:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    break
            self.variables = contexto_anterior
            return resultado
        else:
            print(f"Funci\u00f3n '{nodo.nombre}' no implementada")

    def ejecutar_holobit(self, nodo):
        print(f"Simulando holobit: {nodo.nombre}")
        valores = []
        for v in nodo.valores:
            if isinstance(v, NodoValor):
                valores.append(v.valor)
            else:
                valores.append(v)
        return valores
