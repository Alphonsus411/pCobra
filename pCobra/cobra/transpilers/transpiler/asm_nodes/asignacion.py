from cobra.transpilers.semantica import datos_asignacion


def visit_asignacion(self, nodo):
    """
    Visita y procesa un nodo de asignación.

    Args:
        nodo: Nodo AST que representa una asignación

    Raises:
        ValueError: Si el nodo es None o no es válido
        TypeError: Si el nodo no es del tipo esperado
    """
    if nodo is None:
        raise ValueError("El nodo no puede ser None")

    try:
        nombre, valor, _ = datos_asignacion(self, nodo)
        self.agregar_linea(f"SET {nombre}, {valor}")
    except Exception as e:
        raise ValueError(f"Error al procesar la asignación: {str(e)}")
