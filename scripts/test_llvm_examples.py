#!/usr/bin/env python3
"""Compila y ejecuta los ejemplos LLVM comparando resultados."""

from __future__ import annotations

import subprocess
from pathlib import Path

from cobra.core import Lexer, Parser, TipoToken
from core.ast_nodes import NodoFuncion, NodoValor, NodoOperacionBinaria
from core.interpreter import InterpretadorCobra
from compiler.llvm_backend import generar_ir_funcion

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples" / "llvm"


def run_example(path: Path) -> None:
    code = path.read_text(encoding="utf-8")
    tokens = Lexer(code).analizar_token()
    ast = Parser(tokens).parsear()

    interp = InterpretadorCobra()
    result = None
    for node in ast:
        if isinstance(node, NodoFuncion) and node.nombre == "main" and node.cuerpo:
            instruccion = node.cuerpo[0]
            expr = getattr(instruccion, "expresion", instruccion)
            result = interp.evaluar_expresion(expr)
            break
    if result is None:
        raise RuntimeError(f"No se encontró función main en {path}")

    # Convertir el AST a la representación simple que usa el backend LLVM
    def to_expr(node):
        if isinstance(node, NodoValor):
            return int(node.valor)
        if (
            isinstance(node, NodoOperacionBinaria)
            and node.operador.tipo == TipoToken.SUMA
        ):
            return ("add", to_expr(node.izquierda), to_expr(node.derecha))
        raise NotImplementedError("Expresión no soportada para LLVM")

    llvm_ir = generar_ir_funcion("main", to_expr(expr))
    ll_path = path.with_suffix(".ll")
    ll_path.write_text(llvm_ir, encoding="utf-8")

    bin_path = path.with_suffix("")
    subprocess.run(["clang", ll_path, "-o", bin_path], check=True)
    proc = subprocess.run([bin_path], capture_output=True, text=True)
    ret = proc.returncode

    if ret != result:
        raise RuntimeError(f"Resultado distinto en {path.name}: interp={result}, bin={ret}")
    print(f"{path.name}: OK ({result})")


def main() -> None:
    for cobra_file in sorted(EXAMPLES_DIR.glob("*.cobra")):
        run_example(cobra_file)


if __name__ == "__main__":
    main()
