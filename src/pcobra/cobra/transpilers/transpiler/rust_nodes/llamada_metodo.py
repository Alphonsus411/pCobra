def visit_llamada_metodo(self, nodo):
    if nodo.argumentos:
        raise NotImplementedError(
            f"POO Rust no soporta argumentos en la llamada al método "
            f"'{nodo.nombre_metodo}'; el subconjunto actual admite llamadas sin argumentos."
        )
    objeto = self.obtener_valor(nodo.objeto)
    self.agregar_linea(f"{objeto}.{nodo.nombre_metodo}();")
