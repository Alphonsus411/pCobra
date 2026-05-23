def visit_diccionario(self, nodo):
    elementos_or_pares = getattr(nodo, "elementos", getattr(nodo, "pares", []))
    elementos = ", ".join(
        f"{self.obtener_valor(clave)}: {self.obtener_valor(valor)}"
        for clave, valor in elementos_or_pares
    )
    self.codigo += f"{{{elementos}}}\n"
