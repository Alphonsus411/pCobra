"""Visitadores de asignación para Hololang."""

from cobra.transpilers.semantica import datos_asignacion


def visit_asignacion(self, nodo):
    """Transpila una instrucción de asignación a Hololang."""
    nombre, valor, es_atributo = datos_asignacion(self, nodo)
    tipo = getattr(nodo, "tipo", None)
    if es_atributo:
        declaracion = f"{nombre} = {valor};"
    else:
        prefijo = "let "
        if getattr(nodo, "inferencia", False):
            prefijo = ""
        if tipo:
            declaracion = f"{prefijo}{nombre}: {tipo} = {valor};"
        else:
            declaracion = f"{prefijo}{nombre} = {valor};"
    self.agregar_linea(declaracion)
