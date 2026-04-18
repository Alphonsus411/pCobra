# -*- coding: utf-8 -*-
"""
Herramientas y utilidades para la línea de comandos de Cobra.

Este módulo proporciona las funcionalidades básicas para la interfaz
de línea de comandos del lenguaje Cobra, incluyendo:
- Procesamiento de argumentos
- Gestión de comandos
- Utilidades de CLI
- Selección de *backends* públicos oficiales: ``python``, ``javascript`` y ``rust``.

Tier de soporte de backends:
- Tier 1: ``python``, ``javascript``, ``rust``
- Tier 2: sin targets públicos (reservado para compatibilidad interna/legacy)

Fuente de verdad: ``src/pcobra/cobra/transpilers/targets.py``.

Para más información, consulte la documentación completa.
"""

__version__ = "1.0.0"
__all__ = []  # Definir los elementos públicos del módulo
