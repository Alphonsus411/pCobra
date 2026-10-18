"""Cobertura focal del subconjunto POO Rust de POO-010."""

import pytest

from pcobra.cobra.backends.rust_adapter import RustAdapter
from pcobra.cobra.core.parsing import parsear_codigo_resuelto


def test_backend_rust_emite_clase_sin_estado_desde_fuente_cobra():
    ast = parsear_codigo_resuelto(
        "clase Persona:\n"
        "    metodo inicializar(este):\n"
        "        pasar\n"
        "\n"
        "    metodo saludar(este):\n"
        '        var saludo = "Hola"\n'
        "        imprimir saludo\n"
        "fin\n"
        "var persona = Persona()\n"
        "persona.saludar()\n",
        usar_cache=False,
    )

    salida = RustAdapter().compile(ast)

    assert "struct Persona {}" in salida
    assert "fn new() -> Self" in salida
    assert "fn saludar(&self)" in salida
    assert 'let saludo = "Hola";' in salida
    assert "let persona = Persona::new();" in salida
    assert "persona.saludar();" in salida


def test_backend_rust_diagnostica_atributos_no_soportados():
    ast = parsear_codigo_resuelto(
        "clase Persona:\n"
        "    metodo inicializar(este, nombre):\n"
        "        atributo este nombre = nombre\n"
        "fin\n",
        usar_cache=False,
    )

    with pytest.raises(NotImplementedError, match="atributos de instancia"):
        RustAdapter().compile(ast)
