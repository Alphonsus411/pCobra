from backend.src.core.ast_nodes import NodoAtributo

def visit_asignacion(self, nodo):
    nombre_raw = getattr(nodo, "identificador", getattr(nodo, "variable", None))
    valor = getattr(nodo, "expresion", getattr(nodo, "valor", None))
    if isinstance(nombre_raw, NodoAtributo):
        nombre = self.obtener_valor(nombre_raw)
        self.agregar_linea(f"{nombre} = {self.obtener_valor(valor)};")
    else:
        nombre = nombre_raw
        self.agregar_linea(f"auto {nombre} = {self.obtener_valor(valor)};")
