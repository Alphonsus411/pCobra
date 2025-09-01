def visit_continuar(self, nodo):
    """
    Visita y procesa un nodo de tipo continuar.

    Args:
        nodo: Nodo AST que representa la instrucción continuar

    Raises:
        ValueError: Si el nodo es None o no es válido
    """
    if nodo is None:
        raise ValueError("El nodo no puede ser None")

    try:
        self.agregar_linea("CONTINUE")
    except Exception as e:
        raise ValueError(f"Error al procesar la instrucción continuar: {str(e)}")