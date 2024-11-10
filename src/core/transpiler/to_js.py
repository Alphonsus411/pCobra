from src.core.parser import NodoLista, NodoDiccionario


class TranspiladorJavaScript:
    def __init__(self):
        self.codigo = []

    def transpilar(self, ast_raiz):
        for nodo in ast_raiz:
            self.transpilar_nodo(nodo)
        return "\n".join(self.codigo)

    def transpilar_nodo(self, nodo):
        """Identifica el tipo de nodo y llama al método de transpilación correspondiente."""
        nodo_tipo = type(nodo).__name__

        if nodo_tipo == "NodoAsignacion":
            self.transpilar_asignacion(nodo)
        elif nodo_tipo == "NodoCondicional":
            self.transpilar_condicional(nodo)
        elif nodo_tipo == "NodoBucleMientras":
            self.transpilar_mientras(nodo)
        elif nodo_tipo == "NodoFuncion":
            self.transpilar_funcion(nodo)
        elif nodo_tipo == "NodoLlamadaFuncion":
            self.transpilar_llamada_funcion(nodo)
        elif nodo_tipo == "NodoHolobit":
            self.transpilar_holobit(nodo)
        elif nodo_tipo == "NodoFor":
            self.transpilar_for(nodo)
        elif nodo_tipo == "NodoLista":
            self.transpilar_lista(nodo)
        elif nodo_tipo == "NodoDiccionario":
            self.transpilar_diccionario(nodo)
        elif nodo_tipo == "NodoClase":
            self.transpilar_clase(nodo)
        elif nodo_tipo == "NodoMetodo":
            self.transpilar_metodo(nodo)
        else:
            raise TypeError(f"Tipo de nodo no soportado: {nodo_tipo}")

    # Métodos de transpilación para tipos de nodos básicos

    def transpilar_asignacion(self, nodo):
        """Transpila una asignación en JavaScript."""
        self.codigo.append(f"{nodo.identificador} = {nodo.valor};")

    def transpilar_condicional(self, nodo):
        """Transpila un condicional 'if-else' en JavaScript, admitiendo condiciones compuestas."""
        self.codigo.append(f"if ({nodo.condicion}) {{")
        for instruccion in nodo.cuerpo_si:
            self.transpilar_nodo(instruccion)
        self.codigo.append("}")

        if nodo.cuerpo_sino:
            self.codigo.append("else {")
            for instruccion in nodo.cuerpo_sino:
                self.transpilar_nodo(instruccion)
            self.codigo.append("}")

    def transpilar_mientras(self, nodo):
        """Transpila un bucle 'while' en JavaScript, permitiendo anidación."""
        self.codigo.append(f"while ({nodo.condicion}) {{")
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.codigo.append("}")

    def transpilar_funcion(self, nodo):
        """Transpila una definición de función en JavaScript."""
        parametros = ", ".join(nodo.parametros)
        self.codigo.append(f"function {nodo.nombre}({parametros}) {{")
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.codigo.append("}")

    def transpilar_llamada_funcion(self, nodo):
        """Transpila una llamada a función en JavaScript."""
        parametros = ", ".join(nodo.argumentos)
        self.codigo.append(f"{nodo.nombre}({parametros});")

    def transpilar_holobit(self, nodo):
        """Transpila una asignación de Holobit en JavaScript."""
        valores = ", ".join(map(str, nodo.valores))
        self.codigo.append(f"let {nodo.nombre} = new Holobit([{valores}]);")

    # Métodos de transpilación para nuevas estructuras avanzadas

    def transpilar_for(self, nodo):
        """Transpila un bucle 'for...of' en JavaScript, permitiendo anidación."""
        self.codigo.append(f"for (let {nodo.variable} of {nodo.iterable}) {{")
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.codigo.append("}")

    def transpilar_lista(self, nodo):
        """Transpila una lista en JavaScript, permitiendo anidación."""
        elementos = ", ".join(self.transpilar_elemento(e) for e in nodo.elementos)
        self.codigo.append(f"[{elementos}]")

    def transpilar_diccionario(self, nodo):
        """Transpila un diccionario en JavaScript, permitiendo anidación."""
        pares = ", ".join([f"{clave}: {self.transpilar_elemento(valor)}" for clave, valor in nodo.pares])
        self.codigo.append(f"{{{pares}}}")

    def transpilar_elemento(self, elemento):
        """Transpila un elemento, verificando si es una lista, diccionario o nodo de otro tipo."""
        if isinstance(elemento, NodoLista):
            transpiled_element = []
            self.codigo, original_codigo = transpiled_element, self.codigo
            self.transpilar_lista(elemento)
            self.codigo = original_codigo
            return ''.join(transpiled_element)
        elif isinstance(elemento, NodoDiccionario):
            transpiled_element = []
            self.codigo, original_codigo = transpiled_element, self.codigo
            self.transpilar_diccionario(elemento)
            self.codigo = original_codigo
            return ''.join(transpiled_element)
        else:
            return str(elemento)

    def transpilar_clase(self, nodo):
        """Transpila una clase en JavaScript, admitiendo métodos y clases anidados."""
        self.codigo.append(f"class {nodo.nombre} {{")
        for metodo in nodo.cuerpo:
            self.transpilar_nodo(metodo)
        self.codigo.append("}")

    def transpilar_metodo(self, nodo):
        """Transpila un método de clase, permitiendo anidación."""
        parametros = ", ".join(nodo.parametros)
        self.codigo.append(f"{nodo.nombre}({parametros}) {{")
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.codigo.append("}")
