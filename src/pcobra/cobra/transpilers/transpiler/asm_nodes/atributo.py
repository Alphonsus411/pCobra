def visit_atributo(self, nodo):
    """
    Visita y procesa un nodo de atributo.

    Args:
        nodo: Nodo AST que representa un acceso a atributo

    Raises:
        ValueError: Si el nodo es None o no es válido
        AttributeError: Si faltan atributos requeridos
    """
    if nodo is None:
        raise ValueError("El nodo no puede ser None")

    try:
        valor_objeto = self.obtener_valor(nodo.objeto)
        if not hasattr(nodo, 'nombre'):
            raise AttributeError("El nodo debe tener un atributo 'nombre'")

        self.agregar_linea(f"ATTR {valor_objeto}.{nodo.nombre}")
    except Exception as e:
        raise ValueError(f"Error al procesar el atributo: {str(e)}")