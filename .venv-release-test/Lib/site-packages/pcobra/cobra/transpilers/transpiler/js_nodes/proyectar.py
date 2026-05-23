def visit_proyectar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    modo = self.obtener_valor(nodo.modo)
    self.agregar_linea(f"cobra_proyectar({hb}, {modo});")
