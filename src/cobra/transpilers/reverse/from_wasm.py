# -*- coding: utf-8 -*-
"""Transpilador inverso desde WebAssembly (WASM) a Cobra."""

from __future__ import annotations

from typing import Any, List, Union

from cobra.transpilers.reverse.base import BaseReverseTranspiler
from core.ast_nodes import NodoAsignacion, NodoFuncion, NodoIdentificador, NodoValor

try:
    from wabt import Wabt  # type: ignore
    from sexpdata import loads, Symbol  # type: ignore
except Exception as exc:  # pragma: no cover - dependencias opcionales
    raise ImportError(
        "Se requieren las dependencias 'wabt' y 'sexpdata' para ReverseFromWasm"
    ) from exc


class ReverseFromWasm(BaseReverseTranspiler):
    """Convierte código WASM en nodos del AST de Cobra.

    Este transpilador utiliza `wabt` para decodificar módulos WASM y `sexpdata`
    para procesar la representación en texto (WAT). Actualmente solo soporta
    asignaciones simples de constantes a variables locales.
    """

    def __init__(self) -> None:
        super().__init__()
        self._wabt = Wabt()

    def _to_wat(self, code: Union[str, bytes]) -> str:
        """Obtiene la representación WAT del código WASM."""
        if isinstance(code, bytes):
            return self._wabt.wasm_to_wat(code)
        return code

    def generate_ast(self, code: Union[str, bytes]) -> List[Any]:
        """Genera el AST Cobra desde código WASM o WAT."""
        wat = self._to_wat(code)
        sexp = loads(wat)

        ast: List[Any] = []
        for elem in sexp:
            if isinstance(elem, list) and elem and elem[0] == Symbol("func"):
                nombre = "anon"
                idx = 1
                if len(elem) > 1 and isinstance(elem[1], Symbol) and str(elem[1]).startswith("$"):
                    nombre = str(elem[1])[1:]
                    idx = 2
                cuerpo = self._parse_instructions(elem[idx:])
                ast.append(NodoFuncion(nombre, [], cuerpo))
        self.ast = ast
        return ast

    def _parse_instructions(self, instr: List[Any]) -> List[Any]:
        """Convierte una lista de instrucciones WAT en nodos Cobra."""
        resultado: List[Any] = []
        i = 0
        while i < len(instr):
            actual = instr[i]
            siguiente = instr[i + 1] if i + 1 < len(instr) else None
            if (
                isinstance(actual, list)
                and actual and actual[0] == Symbol("i32.const")
                and isinstance(siguiente, list)
                and siguiente and siguiente[0] == Symbol("local.set")
            ):
                valor = actual[1]
                destino = siguiente[1]
                if isinstance(destino, Symbol):
                    nombre = str(destino)[1:] if str(destino).startswith("$") else str(destino)
                    resultado.append(
                        NodoAsignacion(
                            NodoIdentificador(nombre),
                            NodoValor(valor),
                        )
                    )
                    i += 2
                    continue
            i += 1
        return resultado
