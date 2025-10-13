"""Transpilador que genera un ensamblador simbólico desde Hololang IR."""

from __future__ import annotations


from pcobra.cobra.transpilers.common.utils import BaseTranspiler
from pcobra.core.hololang_ir import (
    HololangAssignment,
    HololangCall,
    HololangExpressionStatement,
    HololangFor,
    HololangFunction,
    HololangHolobit,
    HololangIf,
    HololangModule,
    HololangPrint,
    HololangReturn,
    HololangStatement,
    HololangUnknown,
    HololangWhile,
    build_hololang_ir,
)
from pcobra.core.optimizations import (
    eliminate_common_subexpressions,
    inline_functions,
    optimize_constants,
    remove_dead_code,
)
from pcobra.cobra.macro import expandir_macros


class TranspiladorASM(BaseTranspiler):
    """Genera una salida estilo ensamblador a partir del IR de Hololang."""

    def __init__(self) -> None:
        self._lineas: list[str] = []
        self._indent: int = 0

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def generate_code(self, programa) -> str:
        """Genera el código ensamblador para ``programa``.

        ``programa`` puede ser una lista de nodos AST de Cobra o un módulo de
        IR de Hololang.  Si se proporciona AST, se aplica la misma cadena de
        optimizaciones utilizada por el intérprete antes de construir el IR.
        """

        modulo = self._asegurar_modulo(programa)
        self._lineas = []
        self._indent = 0
        for instruccion in modulo.body:
            self._emitir(instruccion)
        return "\n".join(self._lineas)

    # ------------------------------------------------------------------
    # Conversión y utilidades internas
    # ------------------------------------------------------------------
    def _asegurar_modulo(self, programa) -> HololangModule:
        if isinstance(programa, HololangModule):
            return programa

        nodos = expandir_macros(programa)
        optimizados = remove_dead_code(
            inline_functions(
                eliminate_common_subexpressions(optimize_constants(nodos))
            )
        )
        return build_hololang_ir(optimizados)

    def _agregar_linea(self, texto: str) -> None:
        self._lineas.append("    " * self._indent + texto)

    def _emitir(self, instruccion: HololangStatement) -> None:
        if isinstance(instruccion, HololangAssignment):
            self._agregar_linea(f"SET {instruccion.target}, {instruccion.value}")
            return

        if isinstance(instruccion, HololangIf):
            self._agregar_linea(f"IF {instruccion.condition}")
            self._indent += 1
            for stmt in instruccion.then_branch:
                self._emitir(stmt)
            self._indent -= 1
            if instruccion.else_branch:
                self._agregar_linea("ELSE")
                self._indent += 1
                for stmt in instruccion.else_branch:
                    self._emitir(stmt)
                self._indent -= 1
            self._agregar_linea("END")
            return

        if isinstance(instruccion, HololangWhile):
            self._agregar_linea(f"WHILE {instruccion.condition}")
            self._indent += 1
            for stmt in instruccion.body:
                self._emitir(stmt)
            self._indent -= 1
            self._agregar_linea("END")
            return

        if isinstance(instruccion, HololangFor):
            self._agregar_linea(
                f"FOR {instruccion.target} IN {instruccion.iterable}"
            )
            self._indent += 1
            for stmt in instruccion.body:
                self._emitir(stmt)
            self._indent -= 1
            self._agregar_linea("END")
            return

        if isinstance(instruccion, HololangFunction):
            for decorador in instruccion.decorators:
                self._agregar_linea(f"DECORATOR {decorador}")
            encabezado = "FUNC " + instruccion.name
            if instruccion.parameters:
                encabezado += " " + " ".join(instruccion.parameters)
            if instruccion.async_flag:
                encabezado = "ASYNC " + encabezado
            self._agregar_linea(encabezado)
            self._indent += 1
            for stmt in instruccion.body:
                self._emitir(stmt)
            self._indent -= 1
            self._agregar_linea("ENDFUNC")
            return

        if isinstance(instruccion, HololangReturn):
            if instruccion.value is None:
                self._agregar_linea("RETURN")
            else:
                self._agregar_linea(f"RETURN {instruccion.value}")
            return

        if isinstance(instruccion, HololangCall):
            args = ", ".join(instruccion.arguments)
            sufijo = f" {args}" if args else ""
            self._agregar_linea(f"CALL {instruccion.name}{sufijo}")
            return

        if isinstance(instruccion, HololangExpressionStatement):
            self._agregar_linea(instruccion.expression)
            return

        if isinstance(instruccion, HololangPrint):
            self._agregar_linea(f"PRINT {instruccion.expression}")
            return

        if isinstance(instruccion, HololangHolobit):
            valores = ", ".join(instruccion.values)
            nombre = instruccion.name or "_"
            self._agregar_linea(f"HOLOBIT {nombre} [{valores}]")
            return

        if isinstance(instruccion, HololangUnknown):
            self._agregar_linea(f"; {instruccion.description}")
            return

        raise TypeError(f"Instrucción no soportada: {type(instruccion).__name__}")

