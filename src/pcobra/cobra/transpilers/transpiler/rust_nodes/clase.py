from pcobra.cobra.core.ast_nodes import NodoAtributo, NodoIdentificador


def _contiene_nodo(nodo, tipos, nombres=None):
    visitados = set()

    def visitar(valor):
        identidad = id(valor)
        if identidad in visitados:
            return False
        visitados.add(identidad)
        if isinstance(valor, tipos) and (
            nombres is None or getattr(valor, "nombre", None) in nombres
        ):
            return True
        if isinstance(valor, (list, tuple)):
            return any(visitar(elemento) for elemento in valor)
        if isinstance(valor, dict):
            return any(visitar(elemento) for elemento in valor.values())
        if hasattr(valor, "__dict__"):
            return any(visitar(elemento) for elemento in vars(valor).values())
        return False

    return visitar(nodo)


def _error_poo_rust(nodo, detalle):
    raise NotImplementedError(
        f"POO Rust no soporta {detalle} en la clase '{nodo.nombre}'; "
        "el subconjunto actual admite clases sin estado, un constructor "
        "inicializar(este) vacío y métodos sin argumentos adicionales."
    )


def visit_clase(self, nodo):
    bases = getattr(nodo, "bases", [])
    if bases:
        _error_poo_rust(nodo, "herencia")
    if getattr(nodo, "type_params", []):
        _error_poo_rust(nodo, "clases genéricas")

    metodos = list(getattr(nodo, "metodos", []))
    if _contiene_nodo(metodos, NodoAtributo):
        _error_poo_rust(nodo, "atributos de instancia")
    if _contiene_nodo(metodos, NodoIdentificador, {"este", "self"}):
        _error_poo_rust(nodo, "uso directo del receptor 'este'")

    constructores = [metodo for metodo in metodos if metodo.nombre == "inicializar"]
    if len(constructores) > 1:
        _error_poo_rust(nodo, "constructores múltiples")
    if constructores:
        constructor = constructores[0]
        if constructor.parametros not in (["este"], ["self"]):
            _error_poo_rust(nodo, "parámetros de constructor")
        if any(
            instruccion.__class__.__name__ != "NodoPasar"
            for instruccion in constructor.cuerpo
        ):
            _error_poo_rust(nodo, "cuerpo de constructor con estado")

    self.agregar_linea(f"struct {nodo.nombre} {{}}")
    self.agregar_linea("")
    self.agregar_linea(f"impl {nodo.nombre} {{")
    self.indent += 1
    self.agregar_linea("fn new() -> Self {")
    self.indent += 1
    self.agregar_linea("Self {}")
    self.indent -= 1
    self.agregar_linea("}")
    for metodo in metodos:
        if metodo.nombre == "inicializar":
            continue
        metodo.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
