def visit_hilo(self, nodo):
    self.usa_asyncio = True
    args = ", ".join(self.obtener_valor(a) for a in nodo.llamada.argumentos)
    self.codigo += (
        f"{self.obtener_indentacion()}asyncio.create_task("
        f"{nodo.llamada.nombre}({args}))\n"
    )
