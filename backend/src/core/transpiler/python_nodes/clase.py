def visit_clase(self, nodo):
    metodos = getattr(nodo, "metodos", getattr(nodo, "cuerpo", []))
    self.codigo += f"{self.obtener_indentacion()}class {nodo.nombre}:\n"
    self.nivel_indentacion += 1
    for metodo in metodos:
        metodo.aceptar(self)
    self.nivel_indentacion -= 1
