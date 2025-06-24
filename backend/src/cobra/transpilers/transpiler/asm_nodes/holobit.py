def visit_holobit(self, nodo):
    valores = ", ".join(str(v) for v in nodo.valores)
    if nodo.nombre:
        self.agregar_linea(f"HOLOBIT {nodo.nombre} [{valores}]")
    else:
        self.agregar_linea(f"HOLOBIT [{valores}]")
