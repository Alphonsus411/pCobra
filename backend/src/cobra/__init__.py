"""Paquete de compatibilidad para ejecutar módulos de Cobra."""
import importlib
import sys

# Exponer jupyter_kernel desde el paquete raiz
_jk = importlib.import_module('jupyter_kernel')
sys.modules[__name__ + '.jupyter_kernel'] = _jk

