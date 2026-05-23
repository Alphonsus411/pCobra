from ..visitor import NodeVisitor


class ValidadorBase(NodeVisitor):
    """Validador base para componer una cadena de validadores."""

    def __init__(self):
        self.siguiente = None

    def set_siguiente(self, validador):
        """Establece el siguiente validador en la cadena."""
        self.siguiente = validador
        return validador

    def delegar(self, nodo):
        if self.siguiente is not None:
            nodo.aceptar(self.siguiente)

    def generic_visit(self, node, _visitados_ids=None):
        restaurar_visitados = False
        if _visitados_ids is None:
            _visitados_ids = getattr(self, "_visitados_ids", None)
        if _visitados_ids is None:
            _visitados_ids = set()
            restaurar_visitados = True

        node_id = id(node)
        if node_id in _visitados_ids:
            return

        _visitados_ids.add(node_id)
        self._visitados_ids = _visitados_ids
        try:
            for atributo in getattr(node, "__dict__", {}).values():
                if isinstance(atributo, list):
                    for elem in atributo:
                        if hasattr(elem, "aceptar"):
                            elem.aceptar(self)
                elif hasattr(atributo, "aceptar"):
                    atributo.aceptar(self)
            self.delegar(node)
        finally:
            if restaurar_visitados:
                self._visitados_ids = None
