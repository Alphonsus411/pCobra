def visit_holobit(self, nodo):
    """Transpila una asignación de Holobit en JavaScript."""
    valores = ", ".join(map(str, nodo.valores))
    nombre = getattr(nodo, "nombre", None)
    self.usa_runtime_holobit = True
    if nombre:
        self.agregar_linea(f"let {nombre} = cobra_holobit([{valores}]);")
    else:
        self.agregar_linea(f"cobra_holobit([{valores}]);")
