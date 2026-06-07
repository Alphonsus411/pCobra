def _es_nodo_defer(nodo):
    return nodo.__class__.__name__ == "NodoDefer"


_ATRIBUTOS_AST_CON_DEFER = (
    "instrucciones",
    "cuerpo",
    "bloque_si",
    "bloque_sino",
    "bloque_continuacion",
    "bloque_escape",
    "bloque_try",
    "bloque_catch",
    "bloque_finally",
    "casos",
    "por_defecto",
)


def _contiene_defer(nodo):
    pendientes = [nodo]
    visitados = set()

    while pendientes:
        actual = pendientes.pop()
        if actual is None:
            continue

        if isinstance(actual, (list, tuple)):
            pendientes.extend(actual)
            continue

        identificador = id(actual)
        if identificador in visitados:
            continue
        visitados.add(identificador)

        if _es_nodo_defer(actual):
            return True

        for atributo in _ATRIBUTOS_AST_CON_DEFER:
            if hasattr(actual, atributo):
                valor = getattr(actual, atributo)
                if valor is not None:
                    pendientes.append(valor)

    return False


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

    usa_defer = _contiene_defer(nodo.cuerpo)
    if not usa_defer:
        if not nodo.cuerpo:
            self.codigo += f"{self.obtener_indentacion()}pass\n"
        else:
            for instruccion in nodo.cuerpo:
                instruccion.aceptar(self)
        self.nivel_indentacion -= 1
        return

    nombre_pila = f"__cobra_defer_stack_{self._defer_counter}"
    self._defer_counter += 1
    self._defer_stack.append(nombre_pila)
    try:
        self.usa_contextlib = True
        self.codigo += (
            f"{self.obtener_indentacion()}with contextlib.ExitStack() as {nombre_pila}:\n"
        )
        self.nivel_indentacion += 1
        try:
            if not nodo.cuerpo:
                self.codigo += f"{self.obtener_indentacion()}pass\n"
            else:
                for instruccion in nodo.cuerpo:
                    instruccion.aceptar(self)
        finally:
            self.nivel_indentacion -= 1
    finally:
        self._defer_stack.pop()
        self.nivel_indentacion -= 1
