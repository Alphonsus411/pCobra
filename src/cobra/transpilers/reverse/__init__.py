"""Componentes para convertir código de otros lenguajes a Cobra.

El módulo realiza importaciones seguras de los distintos transpiladores. Si
alguno no puede cargarse por dependencias faltantes, simplemente se ignora para
no impedir el uso de los demás.
"""
from typing import List, Type

from cobra.transpilers.reverse.base import BaseReverseTranspiler
from cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler

# Lista de módulos a intentar importar
_MODULOS = [
    "cobra.transpilers.reverse.from_c",
    "cobra.transpilers.reverse.from_cpp",
    "cobra.transpilers.reverse.from_js",
    "cobra.transpilers.reverse.from_java",
    "cobra.transpilers.reverse.from_go",
    "cobra.transpilers.reverse.from_julia",
    "cobra.transpilers.reverse.from_php",
    "cobra.transpilers.reverse.from_perl",
    "cobra.transpilers.reverse.from_r",
    "cobra.transpilers.reverse.from_ruby",
    "cobra.transpilers.reverse.from_rust",
    "cobra.transpilers.reverse.from_swift",
    "cobra.transpilers.reverse.from_kotlin",
    "cobra.transpilers.reverse.from_fortran",
    "cobra.transpilers.reverse.from_python",
    "cobra.transpilers.reverse.from_asm",
    "cobra.transpilers.reverse.from_cobol",
    "cobra.transpilers.reverse.from_latex",
    "cobra.transpilers.reverse.from_matlab",
    "cobra.transpilers.reverse.from_mojo",
    "cobra.transpilers.reverse.from_pascal",
    "cobra.transpilers.reverse.from_visualbasic",
    "cobra.transpilers.reverse.from_wasm",
]

# Importaciones seguras -------------------------------------------------
for mod_name in list(_MODULOS):
    try:
        module = __import__(mod_name, fromlist=["*"])
        for attr in dir(module):
            if attr.startswith("ReverseFrom"):
                globals()[attr] = getattr(module, attr)
    except Exception:
        _MODULOS.remove(mod_name)

# Clasificación de transpiladores disponibles ---------------------------
TREE_SITTER_TRANSPILERS: List[Type[TreeSitterReverseTranspiler]] = [
    cls
    for cls_name, cls in globals().items()
    if cls_name.startswith("ReverseFrom") and issubclass(cls, TreeSitterReverseTranspiler)
]

CUSTOM_TRANSPILERS: List[Type[BaseReverseTranspiler]] = [
    cls
    for cls_name, cls in globals().items()
    if cls_name.startswith("ReverseFrom") and issubclass(cls, BaseReverseTranspiler)
    and cls not in TREE_SITTER_TRANSPILERS
]

INCOMPLETE_TRANSPILERS: List[Type[BaseReverseTranspiler]] = [
    cls
    for cls in CUSTOM_TRANSPILERS
    if cls.__name__ not in {"ReverseFromPython", "ReverseFromJS", "ReverseFromJava"}
]

__all__ = ["BaseReverseTranspiler", "TreeSitterReverseTranspiler"] + [
    cls.__name__ for cls in TREE_SITTER_TRANSPILERS + CUSTOM_TRANSPILERS
]
