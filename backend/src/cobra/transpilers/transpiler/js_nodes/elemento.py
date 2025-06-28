from backend.src.core.ast_nodes import NodoLista, NodoDiccionario
def visit_elemento(self, elemento):

    """Transpila un elemento o estructura."""
    if isinstance(elemento, NodoLista):
        transpiled_element = []
        self.codigo, original_codigo = transpiled_element, self.codigo
        self.visit_lista(elemento)
        self.codigo = original_codigo
        return ''.join(transpiled_element)
    elif isinstance(elemento, NodoDiccionario):
        transpiled_element = []
        self.codigo, original_codigo = transpiled_element, self.codigo
        self.visit_diccionario(elemento)
        self.codigo = original_codigo
        return ''.join(transpiled_element)
    else:
        return str(elemento)
