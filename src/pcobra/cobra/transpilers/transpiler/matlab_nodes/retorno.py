from pcobra.core.ast_nodes import NodoRetorno


def visit_retorno(self, nodo: NodoRetorno):
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"resultado = {valor};")
