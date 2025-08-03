"""Módulo de análisis semántico y validación para Cobra.

Este módulo proporciona las herramientas necesarias para realizar el análisis
semántico y la validación de módulos en el lenguaje Cobra.

Clases exportadas:
    - Simbolo: Representa un símbolo en la tabla de símbolos
    - Ambito: Maneja el ámbito y alcance de los símbolos
    - AnalizadorSemantico: Realiza el análisis semántico del AST

Funciones exportadas:
    - validar_mod: Valida la estructura de un módulo Cobra
"""
from .analizador import AnalizadorSemantico
from .mod_validator import validar_mod
from .tabla import Ambito, Simbolo

__all__ = ["Simbolo", "Ambito", "AnalizadorSemantico", "validar_mod"]