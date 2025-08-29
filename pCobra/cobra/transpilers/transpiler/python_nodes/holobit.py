def visit_holobit(self, nodo):
    valores = ", ".join(self.obtener_valor(v) for v in nodo.valores)
    if nodo.nombre:
        self.codigo += f"{nodo.nombre} = holobit([{valores}])\n"
    else:
        self.codigo += f"holobit([{valores}])\n"
