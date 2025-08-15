def visit_clase(self, nodo):
    """
    Visita y procesa un nodo de clase.

    Args:
        nodo: Nodo AST que representa una clase

    Raises:
        ValueError: Si el nodo es None o no tiene los atributos requeridos
    """
    if nodo is None:
        raise ValueError("El nodo no puede ser None")

    try:
        nombre = getattr(nodo, 'nombre', None)
        metodos = getattr(nodo, 'metodos', None)

        if nombre is None:
            raise ValueError("El nodo debe tener un atributo 'nombre'")
        if metodos is None:
            raise ValueError("El nodo debe tener un atributo 'metodos'")

        bases = ' '.join(getattr(nodo, 'bases', []))
        extra = f" {bases}" if bases else ""

        self.agregar_linea(f"CLASS {nombre}{extra}")
        self.indent += 1

        try:
            for m in metodos:
                if m is not None:
                    m.aceptar(self)
        finally:
            self.indent -= 1

        self.agregar_linea("ENDCLASS")

    except Exception as e:
        raise ValueError(f"Error al procesar la clase: {str(e)}")