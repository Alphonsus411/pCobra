def visit_funcion(self, nodo):
    for decorador in getattr(nodo, "decoradores", []):
        decorador.aceptar(self)
    parametros = ", ".join(nodo.parametros)
    asincrona = getattr(nodo, "asincronica", False)
    prefijo = "async def" if asincrona else "def"
    if asincrona:
        self.usa_asyncio = True
    genericos = (
        f"[{', '.join(nodo.type_params)}]" if getattr(nodo, "type_params", []) else ""
    )
    self.codigo += (
        f"{self.obtener_indentacion()}{prefijo} {nodo.nombre}{genericos}({parametros}):\n"
    )
    self.nivel_indentacion += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.nivel_indentacion -= 1
