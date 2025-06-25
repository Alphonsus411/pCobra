macros = {}

from backend.src.core.ast_nodes import NodoMacro, NodoLlamadaFuncion

def registrar_macro(nodo: NodoMacro):
    """Registra una macro a partir de su nodo."""
    macros[nodo.nombre] = nodo.cuerpo


def expandir_macros(nodos):
    """Expande macros en una lista de nodos."""
    resultado = []
    for nodo in nodos:
        if isinstance(nodo, NodoMacro):
            registrar_macro(nodo)
            continue
        # Expansión recursiva en listas de atributos
        for atributo, valor in list(getattr(nodo, "__dict__", {}).items()):
            if isinstance(valor, list):
                setattr(nodo, atributo, expandir_macros(valor))
        if isinstance(nodo, NodoLlamadaFuncion) and nodo.nombre in macros:
            cuerpo = macros[nodo.nombre]
            resultado.extend(expandir_macros(cuerpo))
        else:
            resultado.append(nodo)
    return resultado
