class NodeVisitor:
    """Recorre nodos del AST despachando al método adecuado."""

    def visit(self, node):
        """Llama al método ``visit_<Clase>`` correspondiente para ``node``."""
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Método llamado si no existe un ``visit_<Clase>`` específico."""
        raise NotImplementedError(
            f"No se ha implementado visit_{node.__class__.__name__}"
        )
