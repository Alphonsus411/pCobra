def visit_proyectar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    modo = self.obtener_valor(nodo.modo)
    self.codigo += f"{self.obtener_indentacion()}cobra_proyectar({hb}, {modo})\n"
