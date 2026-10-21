from pcobra.cobra.transpilers.semantica import datos_asignacion


def visit_asignacion(self, nodo):
    nombre, valor, es_attr = datos_asignacion(self, nodo)
    if es_attr:
        self.agregar_linea(f"{nombre} = {valor};")
    elif self.variable_rust_declarada(nombre):
        self.agregar_linea(f"{nombre} = {valor};")
    else:
        self.declarar_variable_rust(nombre)
        self.agregar_linea(f"let mut {nombre} = {valor};")
