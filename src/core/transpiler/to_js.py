from src.core.parser import NodoAsignacion, NodoCondicional, NodoBucleMientras, NodoFuncion, NodoLlamadaFuncion, \
    NodoHolobit


class TranspiladorJavaScript:
    def __init__(self):
        self.codigo = []

    def transpilar(self, ast_raiz):
        for nodo in ast_raiz:
            self.transpilar_nodo(nodo)
        return "\n".join(self.codigo)

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
        else:
            raise Exception(f"Tipo de nodo no soportado: {type(nodo).__name__}")

    def transpilar_asignacion(self, nodo):
        self.codigo += f"{nodo.identificador} = {nodo.valor}\n"

    def transpilar_condicional(self, nodo):
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
        self.codigo.append(f"while ({nodo.condicion}) {{")
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.codigo.append("}")

    def transpilar_funcion(self, nodo):
        parametros = ", ".join(nodo.parametros)
        self.codigo.append(f"function {nodo.nombre}({parametros}) {{")
        for instruccion in nodo.cuerpo:
            self.transpilar_nodo(instruccion)
        self.codigo.append("}")

    def transpilar_llamada_funcion(self, nodo):
        parametros = ", ".join(nodo.argumentos)
        self.codigo.append(f"{nodo.nombre}({parametros});")

    def transpilar_holobit(self, nodo):
        self.codigo.append(f"let {nodo.nombre} = new Holobit([{', '.join(map(str, nodo.valores))}]);")
