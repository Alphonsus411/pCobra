from src.core.lexer import Token, TipoToken
from src.core.parser import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoHolobit,
    NodoClase,
    NodoMetodo,
    NodoInstancia,
    NodoAtributo,
    NodoIdentificador,
    NodoValor,
    NodoImprimir,
    NodoRetorno,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoTryCatch,
    NodoThrow,
)


class ExcepcionCobra(Exception):
    def __init__(self, valor):
        super().__init__(valor)
        self.valor = valor


class InterpretadorCobra:
    """Interpreta y ejecuta nodos del lenguaje Cobra."""

    def __init__(self):
        # Pila de contextos para mantener variables locales en cada llamada
        self.contextos = [{}]

    @property
    def variables(self):
        """Devuelve el contexto actual de variables."""
        return self.contextos[-1]

    @variables.setter
    def variables(self, valor):
        """Permite reemplazar el contexto actual."""
        self.contextos[-1] = valor

    def obtener_variable(self, nombre):
        """Busca una variable en la pila de contextos."""
        for contexto in reversed(self.contextos):
            if nombre in contexto:
                return contexto[nombre]
        return None

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
        elif isinstance(nodo, NodoClase):
            self.ejecutar_clase(nodo)
        elif isinstance(nodo, NodoInstancia):
            return self.ejecutar_instancia(nodo)
        elif isinstance(nodo, NodoFuncion):
            self.ejecutar_funcion(nodo)
        elif isinstance(nodo, NodoLlamadaFuncion):
            return self.ejecutar_llamada_funcion(nodo)
        elif isinstance(nodo, NodoLlamadaMetodo):
            return self.ejecutar_llamada_metodo(nodo)
        elif isinstance(nodo, NodoImprimir):
            valor = self.evaluar_expresion(nodo.expresion)
            if isinstance(valor, str):
                if (valor.startswith("\"") and valor.endswith("\"")) or (
                    valor.startswith("'") and valor.endswith("'")
                ):
                    print(valor.strip('"').strip("'"))
                else:
                    obtenido = self.obtener_variable(valor)
                    if obtenido is not None:
                        print(obtenido)
                    else:
                        print(f"Variable '{valor}' no definida")
            else:
                print(valor)
        elif isinstance(nodo, NodoTryCatch):
            return self.ejecutar_try_catch(nodo)
        elif isinstance(nodo, NodoThrow):
            raise ExcepcionCobra(self.evaluar_expresion(nodo.expresion))
        elif isinstance(nodo, NodoHolobit):
            return self.ejecutar_holobit(nodo)
        elif isinstance(nodo, NodoRetorno):
            return self.evaluar_expresion(nodo.expresion)
        elif isinstance(nodo, NodoValor):
            return nodo.valor  # Retorna el valor directo de NodoValor
        else:
            raise ValueError(f"Nodo no soportado: {type(nodo)}")

    def ejecutar_asignacion(self, nodo):
        nombre = getattr(nodo, "identificador", getattr(nodo, "variable", None))
        valor_nodo = getattr(nodo, "expresion", getattr(nodo, "valor", None))
        valor = self.evaluar_expresion(valor_nodo)
        if isinstance(nombre, NodoAtributo):
            objeto = self.evaluar_expresion(nombre.objeto)
            if objeto is None:
                raise ValueError("Objeto no definido para asignación de atributo")
            atributos = objeto.setdefault("__atributos__", {})
            atributos[nombre.nombre] = valor
        else:
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
        elif isinstance(expresion, NodoIdentificador):
            return self.obtener_variable(expresion.nombre)
        elif isinstance(expresion, NodoInstancia):
            return self.ejecutar_instancia(expresion)
        elif isinstance(expresion, NodoAtributo):
            objeto = self.evaluar_expresion(expresion.objeto)
            if objeto is None:
                raise ValueError("Objeto no definido al acceder al atributo")
            atributos = objeto.get("__atributos__", {})
            return atributos.get(expresion.nombre)
        elif isinstance(expresion, NodoHolobit):
            return self.ejecutar_holobit(expresion)
        elif isinstance(expresion, NodoOperacionBinaria):
            izquierda = self.evaluar_expresion(expresion.izquierda)
            derecha = self.evaluar_expresion(expresion.derecha)
            tipo = expresion.operador.tipo
            if tipo == TipoToken.SUMA:
                return izquierda + derecha
            elif tipo == TipoToken.RESTA:
                return izquierda - derecha
            elif tipo == TipoToken.MULT:
                return izquierda * derecha
            elif tipo == TipoToken.DIV:
                return izquierda / derecha
            elif tipo == TipoToken.MOD:
                return izquierda % derecha
            elif tipo == TipoToken.MAYORQUE:
                return izquierda > derecha
            elif tipo == TipoToken.MAYORIGUAL:
                return izquierda >= derecha
            elif tipo == TipoToken.MENORIGUAL:
                return izquierda <= derecha
            elif tipo == TipoToken.IGUAL:
                return izquierda == derecha
            elif tipo == TipoToken.DIFERENTE:
                return izquierda != derecha
            elif tipo == TipoToken.AND:
                return bool(izquierda) and bool(derecha)
            elif tipo == TipoToken.OR:
                return bool(izquierda) or bool(derecha)
            else:
                raise ValueError(f"Operador no soportado: {tipo}")
        elif isinstance(expresion, NodoOperacionUnaria):
            valor = self.evaluar_expresion(expresion.operando)
            tipo = expresion.operador.tipo
            if tipo == TipoToken.NOT:
                return not bool(valor)
            else:
                raise ValueError(f"Operador unario no soportado: {tipo}")
        elif isinstance(expresion, NodoLlamadaMetodo):
            return self.ejecutar_llamada_metodo(expresion)
        elif isinstance(expresion, NodoLlamadaFuncion):
            return self.ejecutar_llamada_funcion(expresion)
        else:
            raise ValueError(f"Expresión no soportada: {expresion}")

    def ejecutar_condicional(self, nodo):
        """Ejecuta un bloque condicional."""
        bloque_si = getattr(nodo, "cuerpo_si", getattr(nodo, "bloque_si", []))
        bloque_sino = getattr(nodo, "cuerpo_sino", getattr(nodo, "bloque_sino", []))
        if self.evaluar_expresion(nodo.condicion):
            for instruccion in bloque_si:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado
        elif bloque_sino:
            for instruccion in bloque_sino:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado

    def ejecutar_mientras(self, nodo):
        # Ejecuta el bucle mientras la condición sea verdadera
        while self.evaluar_expresion(nodo.condicion):
            for instruccion in nodo.cuerpo:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado

    def ejecutar_try_catch(self, nodo):
        try:
            for instruccion in nodo.bloque_try:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado
        except ExcepcionCobra as exc:
            if nodo.nombre_excepcion:
                self.variables[nodo.nombre_excepcion] = exc.valor
            for instruccion in nodo.bloque_catch:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    return resultado

    def ejecutar_funcion(self, nodo):
        # Almacena las funciones definidas por el usuario en el diccionario `variables`
        self.variables[nodo.nombre] = nodo

    def ejecutar_llamada_funcion(self, nodo):
        if nodo.nombre == "imprimir":
            for arg in nodo.argumentos:
                if isinstance(arg, Token) and arg.tipo == TipoToken.IDENTIFICADOR:
                    valor = self.obtener_variable(arg.valor)
                    if valor is None:
                        valor = f"Variable '{arg.valor}' no definida"
                else:
                    valor = self.evaluar_expresion(arg)
                print(valor)
        elif nodo.nombre in self.variables and isinstance(self.variables[nodo.nombre], NodoFuncion):
            funcion = self.variables[nodo.nombre]
            if len(funcion.parametros) != len(nodo.argumentos):
                print(f"Error: se esperaban {len(funcion.parametros)} argumentos")
                return None

            # Crea un nuevo contexto para la llamada
            self.contextos.append({})

            for nombre_param, arg in zip(funcion.parametros, nodo.argumentos):
                self.variables[nombre_param] = self.evaluar_expresion(arg)

            resultado = None
            for instruccion in funcion.cuerpo:
                resultado = self.ejecutar_nodo(instruccion)
                if resultado is not None:
                    break

            # Elimina el contexto al finalizar la función
            self.contextos.pop()
            return resultado
        else:
            print(f"Funci\u00f3n '{nodo.nombre}' no implementada")

    def ejecutar_clase(self, nodo):
        self.variables[nodo.nombre] = nodo

    def ejecutar_instancia(self, nodo):
        clase = self.obtener_variable(nodo.nombre_clase)
        if not isinstance(clase, NodoClase):
            raise ValueError(f"Clase '{nodo.nombre_clase}' no definida")
        return {"__clase__": clase, "__atributos__": {}}

    def ejecutar_llamada_metodo(self, nodo):
        objeto = self.evaluar_expresion(nodo.objeto)
        if not isinstance(objeto, dict) or "__clase__" not in objeto:
            raise ValueError("Objeto inv\u00e1lido en llamada a m\u00e9todo")
        clase = objeto["__clase__"]
        metodo = next((m for m in clase.metodos if m.nombre == nodo.nombre_metodo), None)
        if metodo is None:
            raise ValueError(f"M\u00e9todo '{nodo.nombre_metodo}' no encontrado")

        contexto = {"self": objeto}
        self.contextos.append(contexto)
        for nombre_param, arg in zip(metodo.parametros[1:], nodo.argumentos):
            self.variables[nombre_param] = self.evaluar_expresion(arg)

        resultado = None
        for instruccion in metodo.cuerpo:
            resultado = self.ejecutar_nodo(instruccion)
            if resultado is not None:
                break
        self.contextos.pop()
        return resultado

    def ejecutar_holobit(self, nodo):
        print(f"Simulando holobit: {nodo.nombre}")
        valores = []
        for v in nodo.valores:
            if isinstance(v, NodoValor):
                valores.append(v.valor)
            else:
                valores.append(v)
        return valores
