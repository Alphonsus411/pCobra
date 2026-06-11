import sys
from pathlib import Path

import pytest

# Añadir la ruta del paquete principal
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from pcobra.cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from pcobra.core.ast_nodes import (
    NodoValor,
    NodoAsignacion,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
    NodoIdentificador,
    NodoGarantia,
    NodoRetorno,
    NodoLlamadaFuncion,
)
from pcobra.core.lexer import TipoToken, Token
import pcobra.cobra.core as cobra_core

# Registrar nodos adicionales en el módulo ``cobra.core`` para evitar errores de importación
cobra_core.NodoOperacionBinaria = NodoOperacionBinaria
cobra_core.NodoOperacionUnaria = NodoOperacionUnaria
cobra_core.NodoIdentificador = NodoIdentificador
cobra_core.NodoGarantia = NodoGarantia
cobra_core.NodoRetorno = NodoRetorno


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


def _nodo_garantia_basico() -> NodoGarantia:
    return NodoGarantia(
        NodoIdentificador("ok"),
        [NodoAsignacion("ok", NodoValor(1))],
        [NodoRetorno(NodoValor(0))],
    )


def test_transpilador_python_garantia() -> None:
    nodo = _nodo_garantia_basico()
    transpiler = TranspiladorPython()
    codigo = transpiler.generate_code([nodo])
    assert "if not ok:" in codigo
    assert "return 0" in codigo


def test_transpilador_python_retorno_usa_expresion_y_obtener_valor() -> None:
    class TranspiladorPythonRastreador(TranspiladorPython):
        def __init__(self):
            super().__init__()
            self.tipos_visitados = []

        def obtener_valor(self, nodo):
            self.tipos_visitados.append(type(nodo).__name__)
            return super().obtener_valor(nodo)

    casos = [
        (
            NodoOperacionBinaria(
                NodoIdentificador("n"),
                Token(TipoToken.MULT, "*"),
                NodoValor(2),
            ),
            "return n * 2",
            "NodoOperacionBinaria",
        ),
        (NodoIdentificador("n"), "return n", "NodoIdentificador"),
        (
            NodoLlamadaFuncion("doble", [NodoValor(5)]),
            "return doble(5)",
            "NodoLlamadaFuncion",
        ),
        (
            NodoLlamadaFuncion("identidad", [NodoValor(3)]),
            "return identidad(3)",
            "NodoLlamadaFuncion",
        ),
        (NodoValor(3), "return 3", "NodoValor"),
    ]

    for expresion, salida_esperada, tipo_esperado in casos:
        transpiler = TranspiladorPythonRastreador()
        transpiler.visit_retorno(NodoRetorno(expresion))

        assert transpiler.codigo.strip() == salida_esperada
        assert transpiler.tipos_visitados[0] == tipo_esperado
        assert all(tipo != "NodoRetorno" for tipo in transpiler.tipos_visitados)


def test_transpilador_js_garantia() -> None:
    nodo = _nodo_garantia_basico()
    transpiler = TranspiladorJavaScript()
    codigo = transpiler.generate_code([nodo])
    assert "if (!(ok)) {" in codigo
    assert "return 0" in codigo


def test_transpilador_cpp_garantia() -> None:
    nodo = _nodo_garantia_basico()
    transpiler = TranspiladorCPP()
    codigo = transpiler.generate_code([nodo])
    texto = codigo if isinstance(codigo, str) else "\n".join(codigo)
    assert "if (!(ok)) {" in texto
    assert "return 0" in texto
