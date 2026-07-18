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


_COLECCIONES_AST = (list, tuple, set, frozenset)


def _agregar_hijos_ast_con_defer(pendientes, nodo):
    if isinstance(nodo, dict):
        pendientes.extend(nodo.values())
        return

    if isinstance(nodo, _COLECCIONES_AST):
        pendientes.extend(nodo)
        return

    for atributo in _ATRIBUTOS_AST_CON_DEFER:
        if hasattr(nodo, atributo):
            valor = getattr(nodo, atributo)
            if valor is not None:
                pendientes.append(valor)


def _contiene_defer(nodo):
    """Detecta ``NodoDefer`` en un cuerpo o en bloques de control anidados."""
    pendientes = [nodo]
    visitados = set()

    while pendientes:
        actual = pendientes.pop()
        if actual is None:
            continue

        if isinstance(actual, dict):
            pendientes.extend(actual.values())
            continue

        if isinstance(actual, _COLECCIONES_AST):
            pendientes.extend(actual)
            continue

        identificador = id(actual)
        if identificador in visitados:
            continue
        visitados.add(identificador)

        if _es_nodo_defer(actual):
            return True

        _agregar_hijos_ast_con_defer(pendientes, actual)

    return False


def _emitir_cuerpo_funcion(self, cuerpo):
    if not cuerpo:
        self.codigo += f"{self.obtener_indentacion()}pass\n"
        return

    for instruccion in cuerpo:
        instruccion.aceptar(self)


def visit_funcion(self, nodo):
    for decorador in getattr(nodo, "decoradores", []):
        if decorador.__class__.__name__ == "NodoDecorador":
            decorador.aceptar(self)
        else:
            expr = self.obtener_valor(decorador)
            self.codigo += f"{self.obtener_indentacion()}@{expr}\n"
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
    if asincrona:
        self._async_function_depth += 1

    try:
        usa_defer = _contiene_defer(nodo.cuerpo)
        if not usa_defer:
            _emitir_cuerpo_funcion(self, nodo.cuerpo)
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
                _emitir_cuerpo_funcion(self, nodo.cuerpo)
            finally:
                self.nivel_indentacion -= 1
        finally:
            self._defer_stack.pop()
    finally:
        if asincrona:
            self._async_function_depth -= 1
        self.nivel_indentacion -= 1
