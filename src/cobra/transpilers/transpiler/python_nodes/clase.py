def visit_clase(self, nodo):
    for decorador in getattr(nodo, "decoradores", []):
        decorador.aceptar(self)
    metodos = getattr(nodo, "metodos", getattr(nodo, "cuerpo", []))
    bases = f"({', '.join(nodo.bases)})" if getattr(nodo, 'bases', []) else ""
    genericos = (
        f"[{', '.join(nodo.type_params)}]" if getattr(nodo, "type_params", []) else ""
    )
    self.codigo += f"{self.obtener_indentacion()}class {nodo.nombre}{genericos}{bases}:\n"
    self.nivel_indentacion += 1
    for metodo in metodos:
        metodo.aceptar(self)
    self.nivel_indentacion -= 1
