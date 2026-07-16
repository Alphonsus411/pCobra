def visit_esperar(self, nodo):
    self.usa_asyncio = True
    expr = self.obtener_valor(nodo.expresion)
    if getattr(self, "_async_function_depth", 0) > 0:
        self.codigo += f"{self.obtener_indentacion()}await {expr}\n"
    else:
        self.codigo += f"{self.obtener_indentacion()}asyncio.run({expr})\n"
