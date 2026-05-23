def visit_defer(self, nodo):
    expresion = self.obtener_valor(nodo.expresion)
    nombre = f"_cobra_defer_guard_{self._defer_counter}"
    self._defer_counter += 1
    self.usa_defer_helpers = True
    self.agregar_linea(f"let {nombre} = CobraDefer::new(|| {{ {expresion}; }});")
