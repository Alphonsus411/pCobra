from typing import Any


def visit_try_catch(self, nodo: Any) -> None:
    self.agregar_linea("let resultado: Result<(), Box<dyn std::error::Error>> = (|| {")
    self.indent += 1
    for inst in nodo.bloque_try:
        inst.aceptar(self)
    self.agregar_linea("Ok(())")
    self.indent -= 1
    self.agregar_linea("})();")
    self.agregar_linea("match resultado {")
    self.indent += 1
    self.agregar_linea("Ok(_) => (),")
    self.agregar_linea("Err(e) => {")
    self.indent += 1
    if nodo.nombre_excepcion:
        self.agregar_linea(f"let {nodo.nombre_excepcion} = e;")
    for inst in nodo.bloque_catch:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("},")
    self.indent -= 1
    self.agregar_linea("};")
