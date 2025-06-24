from src.core.ast_nodes import NodoAtributo

def visit_asignacion(self, nodo):
    nombre_raw = getattr(nodo, "identificador", getattr(nodo, "variable", None))
    if isinstance(nombre_raw, NodoAtributo):
        nombre = self.obtener_valor(nombre_raw)
    else:
        nombre = nombre_raw
    valor = getattr(nodo, "expresion", getattr(nodo, "valor", None))
    self.agregar_linea(f"SET {nombre}, {self.obtener_valor(valor)}")
