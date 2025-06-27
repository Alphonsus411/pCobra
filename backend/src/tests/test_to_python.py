from src.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoValor,
    NodoDecorador,
    NodoIdentificador,
    NodoEsperar,
    NodoMetodo,
    NodoClase,
    NodoImprimir,
)
from src.core.ast_nodes import NodoSwitch, NodoCase
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython


def test_transpilador_asignacion():
    ast = [NodoAsignacion("x", NodoValor(10))]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = "from src.core.nativos import *\nx = 10\n"
    assert resultado == esperado


def test_transpilador_condicional():
    ast = [
        NodoCondicional(
            "x > 5",
            [NodoAsignacion("y", NodoValor(2))],
            [NodoAsignacion("y", NodoValor(3))],
        )
    ]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = (
        "from src.core.nativos import *\n"
        "if x > 5:\n    y = 2\nelse:\n    y = 3\n"
    )
    assert resultado == esperado


def test_transpilador_mientras():
    ast = [
        NodoBucleMientras(
            "x > 0", [NodoAsignacion("x", NodoValor("x - 1"))]
        )
    ]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = (
        "from src.core.nativos import *\nwhile x > 0:\n    x = x - 1\n"
    )
    assert resultado == esperado


def test_transpilador_funcion():
    ast = [
        NodoFuncion(
            "miFuncion",
            ["a", "b"],
            [NodoAsignacion("x", NodoValor("a + b"))],
        )
    ]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = (
        "from src.core.nativos import *\n"
        "def miFuncion(a, b):\n    x = a + b\n"
    )
    assert resultado == esperado


def test_transpilador_llamada_funcion():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = "from src.core.nativos import *\nmiFuncion(a, b)\n"
    assert resultado == esperado


def test_transpilador_holobit():
    ast = [NodoHolobit("miHolobit", [0.8, -0.5, 1.2])]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = (
        "from src.core.nativos import *\nmiHolobit = holobit([0.8, -0.5, 1.2])\n"
    )
    assert resultado == esperado


def test_transpilador_switch():
    ast = [
        NodoSwitch(
            "x",
            [
                NodoCase(NodoValor(1), [NodoAsignacion("y", NodoValor(1))]),
                NodoCase(NodoValor(2), [NodoAsignacion("y", NodoValor(2))]),
            ],
            [NodoAsignacion("y", NodoValor(0))],
        )
    ]
    t = TranspiladorPython()
    resultado = t.transpilar(ast)
    esperado = (
        "from src.core.nativos import *\n"
        "match x:\n"
        "    case 1:\n"
        "        y = 1\n"
        "    case 2:\n"
        "        y = 2\n"
        "    case _:\n"
        "        y = 0\n"
    )
    assert resultado == esperado


def test_transpilador_decoradores_anidados():
    decor1 = NodoDecorador(NodoIdentificador("d1"))
    decor2 = NodoDecorador(NodoIdentificador("d2"))
    func = NodoFuncion(
        "saluda",
        [],
        [NodoImprimir(NodoValor("'hola'"))],
        [decor1, decor2],
    )
    codigo = TranspiladorPython().transpilar([func])
    esperado = (
        "from src.core.nativos import *\n"
        "@d1\n"
        "@d2\n"
        "def saluda():\n    print('hola')\n"
    )
    assert codigo == esperado


def test_transpilador_corutina_await():
    f1 = NodoFuncion("saluda", [], [NodoImprimir(NodoValor(1))], asincronica=True)
    f2 = NodoFuncion(
        "principal",
        [],
        [NodoEsperar(NodoLlamadaFuncion("saluda", []))],
        asincronica=True,
    )
    codigo = TranspiladorPython().transpilar([f1, f2])
    esperado = (
        "import asyncio\n"
        "from src.core.nativos import *\n"
        "async def saluda():\n    print(1)\n"
        "async def principal():\n    await saluda()\n"
    )
    assert codigo == esperado


def test_transpilador_clase_compleja():
    metodo = NodoMetodo(
        "run",
        ["self"],
        [NodoEsperar(NodoLlamadaFuncion("tarea", []))],
        asincronica=True,
    )
    clase = NodoClase("Hija", [metodo], ["Base1", "Base2"])
    codigo = TranspiladorPython().transpilar([clase])
    esperado = (
        "import asyncio\n"
        "from src.core.nativos import *\n"
        "class Hija(Base1, Base2):\n"
        "    async def run(self):\n"
        "        await tarea()\n"
    )
    assert codigo == esperado
