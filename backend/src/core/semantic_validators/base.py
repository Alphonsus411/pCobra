from core.visitor import NodeVisitor

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

    def generic_visit(self, nodo):
        for atributo in getattr(nodo, "__dict__", {}).values():
            if isinstance(atributo, list):
                for elem in atributo:
                    if hasattr(elem, "aceptar"):
                        elem.aceptar(self)
            elif hasattr(atributo, "aceptar"):
                atributo.aceptar(self)
        self.delegar(nodo)
