def visit_try_catch(self, nodo):
    self.agregar_linea("TRY")
    self.indent += 1
    for ins in nodo.bloque_try:
        ins.aceptar(self)
    self.indent -= 1
    if nodo.bloque_catch:
        nombre = nodo.nombre_excepcion or ""
        self.agregar_linea(f"CATCH {nombre}")
        self.indent += 1
        for ins in nodo.bloque_catch:
            ins.aceptar(self)
        self.indent -= 1
    self.agregar_linea("ENDTRY")
