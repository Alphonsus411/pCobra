from pcobra.cobra.transpilers.semantica import datos_asignacion


def visit_asignacion(self, nodo):
    """Transpila una asignación en JavaScript."""
    if self.usa_indentacion is None:
        self.usa_indentacion = hasattr(nodo, "variable") or hasattr(
            nodo, "identificador"
        )
    nombre, valor, es_attr = datos_asignacion(self, nodo)
    if es_attr:
        prefijo = ""
    else:
        prefijo = (
            "let "
            if hasattr(nodo, "variable")
            and not getattr(nodo, "inferencia", False)
            and (
                getattr(nodo, "declaracion", False)
                or not self.variable_declarada(nombre)
            )
            else ""
        )
    self.agregar_linea(f"{prefijo}{nombre} = {valor};")
