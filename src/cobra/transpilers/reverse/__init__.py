"""Componentes para convertir código de otros lenguajes a Cobra."""

from typing import List, Type

from cobra.transpilers.reverse.base import BaseReverseTranspiler
from cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler

# Transpiladores implementados con tree-sitter
from cobra.transpilers.reverse.from_c import ReverseFromC
from cobra.transpilers.reverse.from_cpp import ReverseFromCPP
from cobra.transpilers.reverse.from_js import ReverseFromJS
from cobra.transpilers.reverse.from_java import ReverseFromJava
from cobra.transpilers.reverse.from_go import ReverseFromGo
from cobra.transpilers.reverse.from_julia import ReverseFromJulia
from cobra.transpilers.reverse.from_php import ReverseFromPHP
from cobra.transpilers.reverse.from_perl import ReverseFromPerl
from cobra.transpilers.reverse.from_r import ReverseFromR
from cobra.transpilers.reverse.from_ruby import ReverseFromRuby
from cobra.transpilers.reverse.from_rust import ReverseFromRust
from cobra.transpilers.reverse.from_swift import ReverseFromSwift
from cobra.transpilers.reverse.from_kotlin import ReverseFromKotlin
from cobra.transpilers.reverse.from_fortran import ReverseFromFortran

# Transpiladores con implementación personalizada
from cobra.transpilers.reverse.from_python import ReverseFromPython

# Transpiladores sin implementación completa
from cobra.transpilers.reverse.from_asm import ReverseFromASM
from cobra.transpilers.reverse.from_cobol import ReverseFromCOBOL
from cobra.transpilers.reverse.from_latex import ReverseFromLatex
from cobra.transpilers.reverse.from_matlab import ReverseFromMatlab
from cobra.transpilers.reverse.from_mojo import ReverseFromMojo
from cobra.transpilers.reverse.from_pascal import ReverseFromPascal
from cobra.transpilers.reverse.from_visualbasic import ReverseFromVisualBasic
from cobra.transpilers.reverse.from_wasm import ReverseFromWasm

# Agrupar transpiladores por tipo de implementación
TREE_SITTER_TRANSPILERS: List[Type[TreeSitterReverseTranspiler]] = [
    ReverseFromC,
    ReverseFromCPP,
    ReverseFromJS,
    ReverseFromJava,
    ReverseFromGo,
    ReverseFromJulia,
    ReverseFromPHP, 
    ReverseFromPerl,
    ReverseFromR,
    ReverseFromRuby,
    ReverseFromRust,
    ReverseFromSwift,
    ReverseFromKotlin,
    ReverseFromFortran
]

CUSTOM_TRANSPILERS: List[Type[BaseReverseTranspiler]] = [
    ReverseFromPython
]

INCOMPLETE_TRANSPILERS: List[Type[BaseReverseTranspiler]] = [
    ReverseFromASM,
    ReverseFromCOBOL,
    ReverseFromLatex,
    ReverseFromMatlab,
    ReverseFromMojo,
    ReverseFromPascal,
    ReverseFromVisualBasic,
    ReverseFromWasm
]

# Generar __all__ automáticamente
__all__ = ["BaseReverseTranspiler"] + [
    cls.__name__ 
    for transpiler_list in [TREE_SITTER_TRANSPILERS, CUSTOM_TRANSPILERS, INCOMPLETE_TRANSPILERS]
    for cls in transpiler_list
]