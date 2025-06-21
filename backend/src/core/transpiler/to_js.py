from src.core.parser import (
    NodoLista,
    NodoDiccionario,
    NodoValor,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
    NodoAtributo,
    NodoInstancia,
    NodoLlamadaMetodo,
    NodoHilo,
    NodoImport,
    Parser,
)
from src.core.lexer import TipoToken, Lexer


class TranspiladorJavaScript:
    def __init__(self):
        # Incluir importaciones de modulos nativos
        self.codigo = [
            "import * as io from './nativos/io.js';",
            "import * as net from './nativos/io.js';",
            "import * as matematicas from './nativos/matematicas.js';",
            "import { Pila, Cola } from './nativos/estructuras.js';",
        ]
        self.indentacion = 0
        self.usa_indentacion = None

    def agregar_linea(self, linea):
        if self.usa_indentacion:
            self.codigo.append("    " * self.indentacion + linea)
        else:
            self.codigo.append(linea)

    def obtener_valor(self, nodo):
        if isinstance(nodo, NodoValor):
            return str(nodo.valor)
        elif isinstance(nodo, NodoAtributo):
            return f"{self.obtener_valor(nodo.objeto)}.{nodo.nombre}"
        elif isinstance(nodo, NodoInstancia):
            args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
            return f"new {nodo.nombre_clase}({args})"
        elif isinstance(nodo, NodoIdentificador):
            return nodo.nombre
        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.obtener_valor(nodo.izquierda)
            der = self.obtener_valor(nodo.derecha)
            return f"{izq} {nodo.operador.valor} {der}"
        elif isinstance(nodo, NodoOperacionUnaria):
            val = self.obtener_valor(nodo.operando)
            return f"!{val}" if nodo.operador.tipo == TipoToken.NOT else f"{nodo.operador.valor}{val}"
        elif isinstance(nodo, NodoLista) or isinstance(nodo, NodoDiccionario):
            temp = []
            original = self.codigo
            self.codigo = temp
            if isinstance(nodo, NodoLista):
                self.transpilar_lista(nodo)
            else:
                self.transpilar_diccionario(nodo)
            self.codigo = original
            return ''.join(temp)
        else:
            return str(nodo)

    def transpilar(self, ast_raiz):
        for nodo in ast_raiz:
            self.transpilar_nodo(nodo)
        return "\n".join(self.codigo)

    def transpilar_nodo(self, nodo):
        """Identifica el nodo y llama a su método."""
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
        elif nodo_tipo == "NodoHilo":
            self.transpilar_hilo(nodo)
        elif nodo_tipo == "NodoImprimir":
            self.transpilar_imprimir(nodo)
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
        elif nodo_tipo == "NodoInstancia":
            self.agregar_linea(self.obtener_valor(nodo) + ";")
        elif nodo_tipo == "NodoLlamadaMetodo":
            self.transpilar_llamada_metodo(nodo)
        elif nodo_tipo == "NodoRetorno":
            self.transpilar_retorno(nodo)
        elif nodo_tipo == "NodoTryCatch":
            self.transpilar_try_catch(nodo)
        elif nodo_tipo == "NodoThrow":
            self.transpilar_throw(nodo)
        elif nodo_tipo == "NodoImport":
            self.transpilar_import(nodo)
        elif nodo_tipo in ("NodoOperacionBinaria", "NodoOperacionUnaria"):
            self.agregar_linea(self.obtener_valor(nodo))
        else:
            raise TypeError(f"Tipo de nodo no soportado: {nodo_tipo}")

    # Métodos de transpilación para tipos de nodos básicos

    def transpilar_asignacion(self, nodo):
        """Transpila una asignación en JavaScript."""
        if self.usa_indentacion is None:
            self.usa_indentacion = hasattr(nodo, "variable") or hasattr(nodo, "identificador")
        nombre_raw = getattr(nodo, "identificador", getattr(nodo, "variable", None))
        if isinstance(nombre_raw, NodoAtributo):
            nombre = self.obtener_valor(nombre_raw)
            prefijo = ""
        else:
            nombre = nombre_raw
            prefijo = "let " if hasattr(nodo, "variable") else ""
        valor = getattr(nodo, "expresion", getattr(nodo, "valor", None))
        valor = self.obtener_valor(valor)
        self.agregar_linea(f"{prefijo}{nombre} = {valor};")

    def transpilar_condicional(self, nodo):
        """Transpila un 'if-else' con condiciones compuestas."""
        cuerpo_si = getattr(nodo, "cuerpo_si", getattr(nodo, "bloque_si", []))
        cuerpo_sino = getattr(nodo, "cuerpo_sino", getattr(nodo, "bloque_sino", []))
        if self.usa_indentacion is None:
            self.usa_indentacion = any(
                hasattr(ins, "variable") for ins in cuerpo_si + cuerpo_sino
            )
        condicion = self.obtener_valor(nodo.condicion)
        self.agregar_linea(f"if ({condicion}) {{")
        if self.usa_indentacion:
            self.indentacion += 1
        for instruccion in cuerpo_si:
            self.transpilar_nodo(instruccion)
        if self.usa_indentacion:
            self.indentacion -= 1
        if cuerpo_sino:
            if self.usa_indentacion:
                self.agregar_linea("} else {")
            else:
                self.agregar_linea("}")
                self.agregar_linea("else {")
            if self.usa_indentacion:
                self.indentacion += 1
            for instruccion in cuerpo_sino:
                self.transpilar_nodo(instruccion)
            if self.usa_indentacion:
                self.indentacion -= 1
            self.agregar_linea("}")
        else:
            self.agregar_linea("}")

    def transpilar_mientras(self, nodo):
        """Transpila un bucle 'while' en JavaScript, permitiendo anidación."""
        cuerpo = nodo.cuerpo
        if self.usa_indentacion is None:
            self.usa_indentacion = any(hasattr(ins, "variable") for ins in cuerpo)
        condicion = self.obtener_valor(nodo.condicion)
        self.agregar_linea(f"while ({condicion}) {{")
        if self.usa_indentacion:
            self.indentacion += 1
        for instruccion in cuerpo:
            self.transpilar_nodo(instruccion)
        if self.usa_indentacion:
            self.indentacion -= 1
        self.agregar_linea("}")

    def transpilar_funcion(self, nodo):
        """Transpila una definición de función en JavaScript."""
        parametros = ", ".join(nodo.parametros)
        cuerpo = nodo.cuerpo
        if self.usa_indentacion is None:
            self.usa_indentacion = any(hasattr(ins, "variable") for ins in cuerpo)
        self.agregar_linea(f"function {nodo.nombre}({parametros}) {{")
        if self.usa_indentacion:
            self.indentacion += 1
        for instruccion in cuerpo:
            self.transpilar_nodo(instruccion)
        if self.usa_indentacion:
            self.indentacion -= 1
        self.agregar_linea("}")

    def transpilar_llamada_funcion(self, nodo):
        """Transpila una llamada a función en JavaScript."""
        parametros = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
        self.agregar_linea(f"{nodo.nombre}({parametros});")

    def transpilar_hilo(self, nodo):
        args = ", ".join(self.obtener_valor(a) for a in nodo.llamada.argumentos)
        self.agregar_linea(f"Promise.resolve().then(() => {nodo.llamada.nombre}({args}));")

    def transpilar_llamada_metodo(self, nodo):
        args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
        obj = self.obtener_valor(nodo.objeto)
        self.agregar_linea(f"{obj}.{nodo.nombre_metodo}({args});")

    def transpilar_imprimir(self, nodo):
        valor = self.obtener_valor(nodo.expresion)
        self.agregar_linea(f"console.log({valor});")

    def transpilar_retorno(self, nodo):
        valor = self.obtener_valor(nodo.expresion)
        self.agregar_linea(f"return {valor};")

    def transpilar_holobit(self, nodo):
        """Transpila una asignación de Holobit en JavaScript."""
        valores = ", ".join(map(str, nodo.valores))
        nombre = getattr(nodo, "nombre", None)
        if nombre:
            self.agregar_linea(f"let {nombre} = new Holobit([{valores}]);")
        else:
            self.agregar_linea(f"new Holobit([{valores}]);")

    # Métodos de transpilación para nuevas estructuras avanzadas

    def transpilar_for(self, nodo):
        """Transpila un bucle 'for...of' en JavaScript, permitiendo anidación."""
        cuerpo = nodo.cuerpo
        if self.usa_indentacion is None:
            self.usa_indentacion = any(hasattr(ins, "variable") for ins in cuerpo)
        iterable = self.obtener_valor(nodo.iterable)
        self.agregar_linea(f"for (let {nodo.variable} of {iterable}) {{")
        if self.usa_indentacion:
            self.indentacion += 1
        for instruccion in cuerpo:
            self.transpilar_nodo(instruccion)
        if self.usa_indentacion:
            self.indentacion -= 1
        self.agregar_linea("}")

    def transpilar_lista(self, nodo):
        """Transpila una lista en JavaScript, permitiendo anidación."""
        elementos = ", ".join(self.transpilar_elemento(e) for e in nodo.elementos)
        self.agregar_linea(f"[{elementos}]")

    def transpilar_diccionario(self, nodo):
        """Transpila un diccionario en JavaScript, permitiendo anidación."""
        elementos = getattr(nodo, "pares", getattr(nodo, "elementos", []))
        pares = ", ".join([
            f"{clave}: {self.transpilar_elemento(valor)}" for clave, valor in elementos
        ])
        self.agregar_linea(f"{{{pares}}}")

    def transpilar_elemento(self, elemento):
        """Transpila un elemento o estructura."""
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
        metodos = getattr(nodo, "cuerpo", getattr(nodo, "metodos", []))
        if self.usa_indentacion is None:
            self.usa_indentacion = any(hasattr(m, "variable") for m in metodos)
        self.agregar_linea(f"class {nodo.nombre} {{")
        if self.usa_indentacion:
            self.indentacion += 1
        for metodo in metodos:
            self.transpilar_nodo(metodo)
        if self.usa_indentacion:
            self.indentacion -= 1
        self.agregar_linea("}")

    def transpilar_metodo(self, nodo):
        """Transpila un método de clase, permitiendo anidación."""
        parametros = ", ".join(nodo.parametros)
        cuerpo = nodo.cuerpo
        if self.usa_indentacion is None:
            self.usa_indentacion = any(hasattr(ins, "variable") for ins in cuerpo)
        self.agregar_linea(f"{nodo.nombre}({parametros}) {{")
        if self.usa_indentacion:
            self.indentacion += 1
        for instruccion in cuerpo:
            self.transpilar_nodo(instruccion)
        if self.usa_indentacion:
            self.indentacion -= 1
        self.agregar_linea("}")

    def transpilar_try_catch(self, nodo):
        self.agregar_linea("try {")
        if self.usa_indentacion:
            self.indentacion += 1
        for instruccion in nodo.bloque_try:
            self.transpilar_nodo(instruccion)
        if self.usa_indentacion:
            self.indentacion -= 1
        if nodo.bloque_catch:
            catch_var = nodo.nombre_excepcion or ""
            if self.usa_indentacion:
                self.agregar_linea(f"}} catch ({catch_var}) {{")
            else:
                self.agregar_linea("}")
                self.agregar_linea(f"catch ({catch_var}) {{")
            if self.usa_indentacion:
                self.indentacion += 1
            for instruccion in nodo.bloque_catch:
                self.transpilar_nodo(instruccion)
            if self.usa_indentacion:
                self.indentacion -= 1
            self.agregar_linea("}")
        else:
            self.agregar_linea("}")

    def transpilar_throw(self, nodo):
        valor = self.obtener_valor(nodo.expresion)
        self.agregar_linea(f"throw {valor};")

    def transpilar_import(self, nodo):
        """Carga y transpila el módulo indicado."""
        try:
            with open(nodo.ruta, "r", encoding="utf-8") as f:
                codigo = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Módulo no encontrado: {nodo.ruta}")

        lexer = Lexer(codigo)
        tokens = lexer.analizar_token()
        ast = Parser(tokens).parsear()
        for subnodo in ast:
            self.transpilar_nodo(subnodo)
