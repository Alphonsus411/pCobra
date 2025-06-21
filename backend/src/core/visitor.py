import re


class NodeVisitor:
    """Recorre nodos del AST despachando al método adecuado."""

    def _camel_to_snake(self, nombre):
        """Convierte ``NombreClase`` en ``nombre_clase``."""
        nombre = re.sub(r"^Nodo", "", nombre)
        return re.sub(r"(?<!^)(?=[A-Z])", "_", nombre).lower()

    def visit(self, node):
        """Llama al método ``visit_<nombre>`` correspondiente para ``node``."""
        method_name = f"visit_{self._camel_to_snake(node.__class__.__name__)}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Método llamado si no existe un ``visit_<Clase>`` específico."""
        raise NotImplementedError(
            f"No se ha implementado visit_{node.__class__.__name__}"
        )
