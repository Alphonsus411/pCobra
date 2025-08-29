import sys
from pathlib import Path

import pytest

# Añadir la ruta del paquete principal
sys.path.append(str(Path(__file__).resolve().parent.parent / "pCobra"))

from cobra.transpilers.transpiler.to_python import TranspiladorPython
from core.ast_nodes import (
    NodoValor,
    NodoAsignacion,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
)
import cobra.core as cobra_core

# Registrar nodos adicionales en el módulo ``cobra.core`` para evitar errores de importación
cobra_core.NodoOperacionBinaria = NodoOperacionBinaria
cobra_core.NodoOperacionUnaria = NodoOperacionUnaria
cobra_core.NodoIdentificador = NodoIdentificador


def test_generate_code_asignacion_simple() -> None:
    nodo = NodoAsignacion("x", NodoValor(1))
    transpiler = TranspiladorPython()
    codigo = transpiler.generate_code([nodo])
    assert "x = 1" in codigo
    assert transpiler.codigo == codigo


def test_save_file(tmp_path: pytest.TempPathFactory) -> None:
    nodo = NodoAsignacion("x", NodoValor(1))
    transpiler = TranspiladorPython()
    codigo = transpiler.generate_code([nodo])
    archivo = tmp_path / "salida.py"
    transpiler.save_file(str(archivo))
    assert archivo.exists()
    assert archivo.read_text(encoding="utf-8") == codigo
