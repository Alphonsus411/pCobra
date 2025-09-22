def visit_funcion(self, nodo):
    for decorador in getattr(nodo, "decoradores", []):
        decorador.aceptar(self)
    parametros = ", ".join(nodo.parametros)
    asincrona = getattr(nodo, "asincronica", False)
    prefijo = "async def" if asincrona else "def"
    if asincrona:
        self.usa_asyncio = True
    if getattr(nodo, "type_params", []):
        self.usa_typing = True
        for tp in nodo.type_params:
            self.codigo += f"{self.obtener_indentacion()}{tp} = TypeVar('{tp}')\n"
    self.codigo += f"{self.obtener_indentacion()}{prefijo} {nodo.nombre}({parametros}):\n"
    self.nivel_indentacion += 1
    nombre_pila = f"__cobra_defer_stack_{self._defer_counter}"
    self._defer_counter += 1
    self._defer_stack.append(nombre_pila)
    self.usa_contextlib = True
    self.codigo += (
        f"{self.obtener_indentacion()}with contextlib.ExitStack() as {nombre_pila}:\n"
    )
    self.nivel_indentacion += 1
    if not nodo.cuerpo:
        self.codigo += f"{self.obtener_indentacion()}pass\n"
    else:
        for instruccion in nodo.cuerpo:
            instruccion.aceptar(self)
    self.nivel_indentacion -= 1
    self._defer_stack.pop()
    self.nivel_indentacion -= 1
