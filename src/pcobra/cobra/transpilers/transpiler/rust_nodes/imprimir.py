"""Transpilación de NodoImprimir a Rust."""


def visit_imprimir(self, nodo):
    expresion = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f'println!("{{}}", {expresion});')