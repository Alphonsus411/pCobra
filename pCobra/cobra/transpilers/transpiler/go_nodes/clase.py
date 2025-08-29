def visit_clase(self, nodo):
    metodos = getattr(nodo, "metodos", getattr(nodo, "cuerpo", []))
    self.agregar_linea(f"type {nodo.nombre} struct {{}}")
    for metodo in metodos:
        setattr(metodo, "nombre_clase", nodo.nombre)
        metodo.aceptar(self)

