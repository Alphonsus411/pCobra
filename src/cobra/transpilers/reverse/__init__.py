"""Componentes para convertir código de otros lenguajes a Cobra."""

from src.cobra.transpilers.reverse.base import BaseReverseTranspiler
from src.cobra.transpilers.reverse.from_python import ReverseFromPython
from src.cobra.transpilers.reverse.from_c import ReverseFromC
from src.cobra.transpilers.reverse.from_cpp import ReverseFromCPP
from src.cobra.transpilers.reverse.from_js import ReverseFromJS
from src.cobra.transpilers.reverse.from_java import ReverseFromJava
from src.cobra.transpilers.reverse.from_go import ReverseFromGo
from src.cobra.transpilers.reverse.from_julia import ReverseFromJulia
from src.cobra.transpilers.reverse.from_php import ReverseFromPHP
from src.cobra.transpilers.reverse.from_perl import ReverseFromPerl
from src.cobra.transpilers.reverse.from_r import ReverseFromR
from src.cobra.transpilers.reverse.from_ruby import ReverseFromRuby
from src.cobra.transpilers.reverse.from_rust import ReverseFromRust
from src.cobra.transpilers.reverse.from_swift import ReverseFromSwift
from src.cobra.transpilers.reverse.from_kotlin import ReverseFromKotlin
from src.cobra.transpilers.reverse.from_fortran import ReverseFromFortran
from src.cobra.transpilers.reverse.from_asm import ReverseFromASM
from src.cobra.transpilers.reverse.from_cobol import ReverseFromCOBOL
from src.cobra.transpilers.reverse.from_latex import ReverseFromLatex
from src.cobra.transpilers.reverse.from_matlab import ReverseFromMatlab
from src.cobra.transpilers.reverse.from_mojo import ReverseFromMojo
from src.cobra.transpilers.reverse.from_pascal import ReverseFromPascal
from src.cobra.transpilers.reverse.from_visualbasic import ReverseFromVisualBasic
from src.cobra.transpilers.reverse.from_wasm import ReverseFromWasm

__all__ = [
    "BaseReverseTranspiler",
    "ReverseFromPython",
    "ReverseFromC",
    "ReverseFromCPP",
    "ReverseFromJS",
    "ReverseFromJava",
    "ReverseFromGo",
    "ReverseFromJulia",
    "ReverseFromPHP",
    "ReverseFromPerl",
    "ReverseFromR",
    "ReverseFromRuby",
    "ReverseFromRust",
    "ReverseFromSwift",
    "ReverseFromKotlin",
    "ReverseFromFortran",
    "ReverseFromASM",
    "ReverseFromCOBOL",
    "ReverseFromLatex",
    "ReverseFromMatlab",
    "ReverseFromMojo",
    "ReverseFromPascal",
    "ReverseFromVisualBasic",
    "ReverseFromWasm",
]
