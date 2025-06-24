def visit_holobit(self, nodo):
    valores = ", ".join(str(v) for v in nodo.valores)
    if getattr(nodo, "nombre", None):
        self.agregar_linea(f"let {nodo.nombre} = holobit(vec![{valores}]);")
    else:
        self.agregar_linea(f"holobit(vec![{valores}]);")
