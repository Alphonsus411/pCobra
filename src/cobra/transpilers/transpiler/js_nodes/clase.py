def visit_clase(self, nodo):
    """Transpila una clase en JavaScript, admitiendo métodos y clases anidados."""
    metodos = getattr(nodo, "cuerpo", getattr(nodo, "metodos", []))
    if self.usa_indentacion is None:
        self.usa_indentacion = any(hasattr(m, "variable") for m in metodos)
    bases = getattr(nodo, "bases", [])
    base = f" extends {bases[0]}" if bases else ""
    extra = f" /* bases: {', '.join(bases)} */" if len(bases) > 1 else ""
    if getattr(nodo, "type_params", []):
        self.agregar_linea(
            f"// Generics {', '.join(nodo.type_params)} no soportados en JavaScript"
        )
    self.agregar_linea(f"class {nodo.nombre}{base} {{{extra}")
    if self.usa_indentacion:
        self.indentacion += 1
    for metodo in metodos:
        if hasattr(metodo, "aceptar"):
            metodo.aceptar(self)
        else:
            nombre = metodo.__class__.__name__
            if nombre.startswith("Nodo"):
                nombre = nombre[4:]
            visit = getattr(self, f"visit_{nombre.lower()}", None)
            if visit:
                visit(metodo)
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")
    for metodo in metodos:
        for decorador in reversed(getattr(metodo, "decoradores", [])):
            expr = self.obtener_valor(decorador.expresion)
            self.agregar_linea(
                (
                    f"{nodo.nombre}.prototype.{metodo.nombre} = "
                    f"{expr}({nodo.nombre}.prototype.{metodo.nombre});"
                )
            )
    for decorador in reversed(getattr(nodo, "decoradores", [])):
        expr = self.obtener_valor(decorador.expresion)
        self.agregar_linea(f"{nodo.nombre} = {expr}({nodo.nombre});")
