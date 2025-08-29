def visit_holobit(self, nodo):
    """Transpila una asignación de Holobit en JavaScript."""
    valores = ", ".join(map(str, nodo.valores))
    nombre = getattr(nodo, "nombre", None)
    if nombre:
        self.agregar_linea(f"let {nombre} = new Holobit([{valores}]);")
    else:
        self.agregar_linea(f"new Holobit([{valores}]);")
