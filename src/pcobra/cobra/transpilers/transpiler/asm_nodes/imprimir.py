from cobra.core.ast_nodes import NodoValor


def visit_imprimir(self, nodo):
    texto = (
        nodo.expresion.valor
        if isinstance(nodo.expresion, NodoValor)
        else self.obtener_valor(nodo.expresion)
    )
    etiqueta = self.nueva_cadena(str(texto))
    self.agregar_linea("mov rax, 1")
    self.agregar_linea("mov rdi, 1")
    self.agregar_linea(f"mov rsi, {etiqueta}")
    self.agregar_linea(f"mov rdx, {etiqueta}_len")
    self.agregar_linea("syscall")
