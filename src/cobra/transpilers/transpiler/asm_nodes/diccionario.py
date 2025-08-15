def visit_diccionario(self, nodo):
    """
    Visita y procesa un nodo de diccionario.

    Args:
        nodo: Nodo AST que representa un diccionario

    Raises:
        ValueError: Si el nodo es None o no es válido
    """
    if nodo is None:
        raise ValueError("El nodo no puede ser None")

    try:
        if not hasattr(nodo, 'elementos'):
            raise AttributeError("El nodo debe tener un atributo 'elementos'")

        pares = ", ".join(
            f"{self.obtener_valor(k)}:{self.obtener_valor(v)}"
            for k, v in nodo.elementos
        )
        self.agregar_linea(f"{{{pares}}}")

    except Exception as e:
        raise ValueError(f"Error al procesar el diccionario: {str(e)}")