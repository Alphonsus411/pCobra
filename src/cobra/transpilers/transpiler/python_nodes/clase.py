def visit_clase(self, nodo):
    for decorador in getattr(nodo, "decoradores", []):
        decorador.aceptar(self)
    metodos = getattr(nodo, "metodos", getattr(nodo, "cuerpo", []))
    bases_lista = list(getattr(nodo, "bases", []))
    if getattr(nodo, "type_params", []):
        self.usa_typing = True
        for tp in nodo.type_params:
            self.codigo += f"{self.obtener_indentacion()}{tp} = TypeVar('{tp}')\n"
        bases_lista.insert(0, f"Generic[{', '.join(nodo.type_params)}]")
    bases = f"({', '.join(bases_lista)})" if bases_lista else ""
    self.codigo += f"{self.obtener_indentacion()}class {nodo.nombre}{bases}:\n"
    self.nivel_indentacion += 1
    for metodo in metodos:
        metodo.aceptar(self)
    self.nivel_indentacion -= 1
