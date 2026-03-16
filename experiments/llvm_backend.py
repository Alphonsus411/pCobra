"""Generación sencilla de IR para LLVM."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple, Union

Expr = Union[int, Tuple[str, "Expr", "Expr"]]


@dataclass
class LLVMBackend:
    """Backend minimalista que genera fragmentos de LLVM IR.

    Solo se soportan expresiones con enteros y sumas binarias.
    """

    counter: int = 0
    instrucciones: List[str] = field(default_factory=list)

    def _temp(self) -> str:
        """Devuelve el nombre de un registro temporal nuevo."""
        self.counter += 1
        return f"%t{self.counter}"

    def emitir(self, linea: str) -> None:
        self.instrucciones.append(linea)

    def generar_expresion(self, expr: Expr) -> str:
        """Genera IR para ``expr`` y devuelve el registro con el resultado."""
        if isinstance(expr, int):
            temp = self._temp()
            self.emitir(f"{temp} = add i32 0, {expr}")
            return temp
        if isinstance(expr, tuple) and len(expr) == 3 and expr[0] == "add":
            izquierda = self.generar_expresion(expr[1])
            derecha = self.generar_expresion(expr[2])
            temp = self._temp()
            self.emitir(f"{temp} = add i32 {izquierda}, {derecha}")
            return temp
        raise NotImplementedError("Expresión no soportada")

    def generar_funcion(self, nombre: str, expr: Expr) -> str:
        """Crea una función que evalúa ``expr`` y retorna el resultado."""
        self.instrucciones.clear()
        resultado = self.generar_expresion(expr)
        cuerpo = "\n  ".join(self.instrucciones)
        return (
            f"define i32 @{nombre}() {{\n  {cuerpo}\n  ret i32 {resultado}\n}}"
        )


def generar_ir_expresion(expr: Expr) -> str:
    """Devuelve el código LLVM IR para una expresión simple."""
    backend = LLVMBackend()
    backend.generar_expresion(expr)
    return "\n".join(backend.instrucciones)


def generar_ir_funcion(nombre: str, expr: Expr) -> str:
    """Devuelve el IR de una función sin parámetros que retorna ``expr``."""
    backend = LLVMBackend()
    return backend.generar_funcion(nombre, expr)

