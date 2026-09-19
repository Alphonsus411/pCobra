from __future__ import annotations


def visit_enum(self, nodo):
    """Genera la definición de un ``enum`` sencillo."""
    self.codigo += f"{self.obtener_indentacion()}class {nodo.nombre}:\n"
    self.nivel_indentacion += 1
    if not nodo.miembros:
        self.codigo += f"{self.obtener_indentacion()}pass\n"
    else:
        for idx, miembro in enumerate(nodo.miembros):
            self.codigo += f"{self.obtener_indentacion()}{miembro} = {idx}\n"
    self.nivel_indentacion -= 1
