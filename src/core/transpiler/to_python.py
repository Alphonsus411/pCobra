from src.core.parser import NodoAsignacion, NodoCondicional, NodoBucleMientras, NodoFuncion, NodoLlamadaFuncion, \
    NodoHolobit


class TranspiladorPython:
    def __init__(self):
        self.codigo = ""

    def transpilar(self, ast):
        for nodo in ast:
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

    # En to_python.py
    def transpilar_asignacion(self, nodo):
        self.codigo += f"{nodo.nombre} = {nodo.valor}\n"

    def transpilar_condicional(self, nodo):
        self.codigo += f"if {nodo.condicion}:\n"
        for instruccion in nodo.bloque_si:
            self.codigo += "    "
            self.transpilar_nodo(instruccion)
        if nodo.bloque_sino:
            self.codigo += "else:\n"
            for instruccion in nodo.bloque_sino:
                self.codigo += "    "
                self.transpilar_nodo(instruccion)

    def transpilar_mientras(self, nodo):
        self.codigo += f"while {nodo.condicion}:\n"
        for instruccion in nodo.cuerpo:
            self.codigo += "    "
            self.transpilar_nodo(instruccion)

    def transpilar_funcion(self, nodo):
        self.codigo += f"def {nodo.nombre}({', '.join(nodo.parametros)}):\n"
        for instruccion in nodo.cuerpo:
            self.codigo += "    "
            self.transpilar_nodo(instruccion)

    def transpilar_llamada_funcion(self, nodo):
        self.codigo += f"{nodo.nombre}({', '.join(nodo.argumentos)})"

    # En to_python.py
    def transpilar_holobit(self, nodo):
        self.codigo += f"holobit({nodo.nombre})\n"


