def visit_holobit(self, nodo):
    valores = ", ".join(self.obtener_valor(v) for v in nodo.valores)
    self.usa_runtime_holobit = True
    if nodo.nombre:
        self.codigo += f"{nodo.nombre} = cobra_holobit([{valores}])\n"
    else:
        self.codigo += f"cobra_holobit([{valores}])\n"
