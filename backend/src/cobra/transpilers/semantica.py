from backend.src.core.ast_nodes import NodoAtributo


def datos_asignacion(transpilador, nodo):
    """Obtiene el nombre y el valor de una asignación.

    Devuelve una tupla ``(nombre, valor, es_atributo)`` donde ``nombre`` y
    ``valor`` ya están procesados mediante ``transpilador.obtener_valor``.
    ``es_atributo`` indica si el identificador era un atributo del AST.
    """
    nombre_raw = getattr(nodo, "identificador", getattr(nodo, "variable", None))
    valor_nodo = getattr(nodo, "expresion", getattr(nodo, "valor", None))
    es_atributo = isinstance(nombre_raw, NodoAtributo)
    if es_atributo:
        nombre = transpilador.obtener_valor(nombre_raw)
    else:
        nombre = nombre_raw
    valor = transpilador.obtener_valor(valor_nodo)
    return nombre, valor, es_atributo


def _inc_indent(transpilador):
    if hasattr(transpilador, "usa_indentacion"):
        if transpilador.usa_indentacion:
            transpilador.indentacion += 1
    elif hasattr(transpilador, "indentacion"):
        transpilador.indentacion += 1
    elif hasattr(transpilador, "indent"):
        transpilador.indent += 1
    elif hasattr(transpilador, "nivel_indentacion"):
        transpilador.nivel_indentacion += 1


def _dec_indent(transpilador):
    if hasattr(transpilador, "usa_indentacion"):
        if transpilador.usa_indentacion:
            transpilador.indentacion -= 1
    elif hasattr(transpilador, "indentacion"):
        transpilador.indentacion -= 1
    elif hasattr(transpilador, "indent"):
        transpilador.indent -= 1
    elif hasattr(transpilador, "nivel_indentacion"):
        transpilador.nivel_indentacion -= 1


def procesar_bloque(transpilador, cuerpo):
    """Ejecuta el cuerpo de un bloque aumentando la indentación de forma genérica."""
    _inc_indent(transpilador)
    for instruccion in cuerpo:
        instruccion.aceptar(transpilador)
    _dec_indent(transpilador)
