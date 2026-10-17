"""Cobertura focal de POO-009 para la frontera JavaScript."""

from pcobra.cobra.backends.javascript_adapter import JavaScriptAdapter
from pcobra.cobra.core.parsing import parsear_codigo_resuelto


def test_backend_javascript_adapta_poo_desde_fuente_cobra():
    ast = parsear_codigo_resuelto(
        "clase Persona:\n"
        "    metodo inicializar(este, nombre):\n"
        "        atributo este nombre = nombre\n"
        "\n"
        "    metodo saludar(este):\n"
        "        imprimir \"Hola \" + atributo este nombre\n"
        "fin\n"
        "var persona = Persona(\"Adolfo\")\n"
        "persona.saludar()\n",
        usar_cache=False,
    )

    salida = JavaScriptAdapter().compile(ast)

    assert "constructor(nombre) {" in salida
    assert "inicializar(" not in salida
    assert "este" not in salida
    assert "this.nombre = nombre;" in salida
    assert "new Persona('Adolfo')" in salida
    assert "persona.saludar();" in salida
