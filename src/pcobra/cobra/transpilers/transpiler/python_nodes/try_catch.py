def _contiene_nombre(valor, nombre, visitados=None):
    if valor == nombre:
        return True
    if isinstance(valor, str) or valor is None:
        return False

    if visitados is None:
        visitados = set()
    identificador = id(valor)
    if identificador in visitados:
        return False
    visitados.add(identificador)

    if isinstance(valor, (list, tuple)):
        return any(_contiene_nombre(elemento, nombre, visitados) for elemento in valor)
    if hasattr(valor, "__dict__"):
        return any(
            _contiene_nombre(elemento, nombre, visitados)
            for elemento in vars(valor).values()
        )
    return False


def _generar_nombre_excepcion_temporal(self, nodo):
    base = "__cobra_excepcion_temporal"
    nombre = base
    sufijo = 0
    nombres_reservados = getattr(self, "_nombres_identificadores", set())
    while (
        nombre in nombres_reservados
        or nombre in self.codigo
        or _contiene_nombre(nodo, nombre)
    ):
        sufijo += 1
        nombre = f"{base}_{sufijo}"
    return nombre


def visit_try_catch(self, nodo):
    self.codigo += f"{self.obtener_indentacion()}try:\n"
    self.nivel_indentacion += 1
    for instruccion in nodo.bloque_try:
        instruccion.aceptar(self)
    self.nivel_indentacion -= 1
    if nodo.nombre_excepcion is not None:
        conserva_excepcion = nodo.nombre_excepcion and nodo.bloque_finally
        nombre_temporal = (
            _generar_nombre_excepcion_temporal(self, nodo)
            if conserva_excepcion
            else nodo.nombre_excepcion
        )
        nombre = f" as {nombre_temporal}" if nombre_temporal else ""
        self.codigo += f"{self.obtener_indentacion()}except Exception{nombre}:\n"
        self.nivel_indentacion += 1
        if conserva_excepcion:
            self.codigo += (
                f"{self.obtener_indentacion()}{nodo.nombre_excepcion} = "
                f"{nombre_temporal}\n"
            )
        for instruccion in nodo.bloque_catch:
            instruccion.aceptar(self)
        self.nivel_indentacion -= 1
    if nodo.bloque_finally:
        self.codigo += f"{self.obtener_indentacion()}finally:\n"
        self.nivel_indentacion += 1
        for instruccion in nodo.bloque_finally:
            instruccion.aceptar(self)
        self.nivel_indentacion -= 1
