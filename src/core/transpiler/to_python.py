from src.core.parser import (
    NodoAsignacion, NodoCondicional, NodoBucleMientras, NodoFuncion,
    NodoLlamadaFuncion, NodoHolobit, NodoFor, NodoLista, NodoDiccionario,
    NodoClase, NodoMetodo, NodoValor
)


class TranspiladorPython:
    def __init__(self):
        self.codigo = ""
        self.nivel_indentacion = 0

    def obtener_indentacion(self):
        return "    " * self.nivel_indentacion

    def transpilar(self, nodos):
        for nodo in nodos:
            self.transpilar_nodo(nodo)
        return self.codigo

    def transpilar_nodo(self, nodo):
        if isinstance(nodo, NodoAsignacion):
            self.transpilar_asignacion(nodo)
        elif isinstance(nodo, NodoCondicional):
            self.transpilar_condicional(nodo)
        elif isinstance(nodo, NodoBucleMientras):
            self.transpilar_mientras(nodo)
        elif isinstance(nodo, NodoFuncion):
            self.transpilar_funcion(nodo)
        elif isinstance(nodo, NodoLlamadaFuncion):
            self.transpilar_llamada_funcion(nodo)
        elif isinstance(nodo, NodoHolobit):
            self.transpilar_holobit(nodo)
        elif isinstance(nodo, NodoFor):
            self.transpilar_for(nodo)
        elif isinstance(nodo, NodoLista):
            self.transpilar_lista(nodo)
        elif isinstance(nodo, NodoDiccionario):
            self.transpilar_diccionario(nodo)
        elif isinstance(nodo, NodoClase):
            self.transpilar_clase(nodo)
        elif isinstance(nodo, NodoMetodo):
            self.transpilar_metodo(nodo)
        elif isinstance(nodo, NodoValor):
            self.codigo += self.obtener_valor(nodo)
        else:
            raise TypeError(f"Tipo de nodo no soportado: {type(nodo).__name__}")

    def obtener_valor(self, nodo):
        return str(nodo.valor) if isinstance(nodo, NodoValor) else str(nodo)

    def transpilar_asignacion(self, nodo):
        self.codigo += (
            f"{self.obtener_indentacion()}{nodo.variable} = "
            f"{self.obtener_valor(nodo.expresion)}\n"
        )

    def transpilar_condicional(self, nodo):
        self.codigo += f"{self.obtener_indentacion()}if {nodo.condicion}:\n"
        self.nivel_indentacion += 1
        for instruccion in nodo.bloque_si:
            self.transpilar_nodo(instruccion)
        self.nivel_indentacion -= 1
        if nodo.bloque_sino:
            self.codigo += f"{self.obtener_indentacion()}else:\n"
            self.nivel_indentacion += 1
            for instruccion in nodo.bloque_sino:
                self.transpilar_nodo(instruccion)
            self.nivel_indentacion -= 1

    def transpilar_mientras(self, nodo):
        self.codigo += f"{self.obtener_indentacion()}while {nodo.condicion}:\n"
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.nivel_indentacion -= 1

    def transpilar_for(self, nodo):
        self.codigo += (
            f"{self.obtener_indentacion()}for {nodo.variable} in "
            f"{nodo.iterable}:\n"
        )
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.nivel_indentacion -= 1

    def transpilar_funcion(self, nodo):
        parametros = ", ".join(nodo.parametros)
        self.codigo += f"{self.obtener_indentacion()}def {nodo.nombre}({parametros}):\n"
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.nivel_indentacion -= 1

    def transpilar_llamada_funcion(self, nodo):
        argumentos = ", ".join(nodo.argumentos)
        self.codigo += f"{nodo.nombre}({argumentos})\n"

    def transpilar_holobit(self, nodo):
        valores = ", ".join(self.obtener_valor(valor) for valor in nodo.valores)
        self.codigo += f"holobit([{valores}])\n"

    def transpilar_lista(self, nodo):
        elementos = ", ".join(
            self.obtener_valor(elemento) for elemento in nodo.elementos
        )
        self.codigo += f"[{elementos}]\n"

    def transpilar_diccionario(self, nodo):
        # Corrección: `elementos` es una lista de pares clave-valor
        elementos = ", ".join(
            f"{self.obtener_valor(clave)}: {self.obtener_valor(valor)}"
            for clave, valor in nodo.elementos
        )
        self.codigo += f"{{{elementos}}}\n"

    def transpilar_clase(self, nodo):
        self.codigo += f"{self.obtener_indentacion()}class {nodo.nombre}:\n"
        self.nivel_indentacion += 1
        for metodo in nodo.metodos:
            self.transpilar_metodo(metodo)
        self.nivel_indentacion -= 1

    def transpilar_metodo(self, nodo):
        parametros = ", ".join(nodo.parametros)
        self.codigo += f"{self.obtener_indentacion()}def {nodo.nombre}({parametros}):\n"
        self.nivel_indentacion += 1
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.nivel_indentacion -= 1