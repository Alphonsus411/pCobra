from core.ast_nodes import (
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
    NodoPasar,
    NodoExport,
)
from core.ast_nodes import NodoSwitch, NodoCase, NodoPattern, NodoGuard
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.import_helper import get_standard_imports
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser

IMPORTS = get_standard_imports("python")


def test_transpilador_asignacion():
    ast = [NodoAsignacion("x", NodoValor(10))]
    transpilador = TranspiladorPython()
    resultado = transpilador.generate_code(ast)
    esperado = IMPORTS + "x = 10\n"
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
    resultado = transpilador.generate_code(ast)
    esperado = (
        IMPORTS
        + "if x > 5:\n    y = 2\nelse:\n    y = 3\n"
    )
    assert resultado == esperado


def test_transpilador_mientras():
    ast = [
        NodoBucleMientras(
            "x > 0", [NodoAsignacion("x", NodoValor("x - 1"))]
        )
    ]
    transpilador = TranspiladorPython()
    resultado = transpilador.generate_code(ast)
    esperado = (
        IMPORTS + "while x > 0:\n    x = x - 1\n"
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
    resultado = transpilador.generate_code(ast)
    esperado = (
        IMPORTS
        + "def miFuncion(a, b):\n    x = a + b\n"
    )
    assert resultado == esperado


def test_export():
    ast = [
        NodoFuncion("saluda", [], [NodoPasar()]),
        NodoExport("saluda"),
    ]
    transpilador = TranspiladorPython()
    resultado = transpilador.generate_code(ast)
    esperado = (
        IMPORTS
        + "def saluda():\n    pass\n__all__ = ['saluda']\n"
    )
    assert resultado == esperado


def test_transpilador_llamada_funcion():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    transpilador = TranspiladorPython()
    resultado = transpilador.generate_code(ast)
    esperado = IMPORTS + "miFuncion(a, b)\n"
    assert resultado == esperado


def test_transpilador_holobit():
    ast = [NodoHolobit("miHolobit", [0.8, -0.5, 1.2])]
    transpilador = TranspiladorPython()
    resultado = transpilador.generate_code(ast)
    esperado = (
        IMPORTS + "miHolobit = holobit([0.8, -0.5, 1.2])\n"
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
    resultado = t.generate_code(ast)
    esperado = (
        IMPORTS
        + "match x:\n"
        + "    case 1:\n"
        + "        y = 1\n"
        + "    case 2:\n"
        + "        y = 2\n"
        + "    case _:\n"
        + "        y = 0\n"
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
    codigo = TranspiladorPython().generate_code([func])
    esperado = (
        IMPORTS
        + "@d1\n"
        + "@d2\n"
        + "def saluda():\n    print('hola')\n"
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
    codigo = TranspiladorPython().generate_code([f1, f2])
    esperado = (
        "import asyncio\n"
        + IMPORTS
        + "async def saluda():\n    print(1)\n"
        + "async def principal():\n    await saluda()\n"
    )
    assert codigo == esperado


def test_transpilador_switch_patron_guardia():
    patron_interno = NodoPattern([
        NodoPattern(NodoIdentificador("y")),
        NodoPattern("_"),
    ])
    patron_principal = NodoPattern([
        NodoPattern(NodoIdentificador("x")),
        patron_interno,
    ])
    caso = NodoCase(
        NodoGuard(patron_principal, NodoValor("x > y")),
        [NodoAsignacion("z", NodoValor(1))],
    )
    ast = [
        NodoSwitch(
            "punto",
            [caso],
            [NodoAsignacion("z", NodoValor(0))],
        )
    ]
    t = TranspiladorPython()
    resultado = t.generate_code(ast)
    esperado = (
        IMPORTS
        + "match punto:\n"
        + "    case (x, (y, _)) if x > y:\n"
        + "        z = 1\n"
        + "    case _:\n"
        + "        z = 0\n"
    )
    assert resultado == esperado


def test_transpilador_clase_compleja():
    metodo = NodoMetodo(
        "run",
        ["self"],
        [NodoEsperar(NodoLlamadaFuncion("tarea", []))],
        asincronica=True,
    )
    clase = NodoClase("Hija", [metodo], ["Base1", "Base2"])
    codigo = TranspiladorPython().generate_code([clase])
    esperado = (
        "import asyncio\n"
        + IMPORTS
        + "class Hija(Base1, Base2):\n"
        + "    async def run(self):\n"
        + "        await tarea()\n"
    )
    assert codigo == esperado

def test_decoradores_en_clase_y_metodo():
    decor = NodoDecorador(NodoIdentificador("dec"))
    metodo = NodoMetodo("run", ["self"], [NodoPasar()], asincronica=True)
    metodo.decoradores = [decor]
    clase = NodoClase("C", [metodo])
    clase.decoradores = [decor]
    codigo = TranspiladorPython().generate_code([clase])
    esperado = (
        "import asyncio\n"
        + IMPORTS
        + "@dec\n"
        + "class C:\n"
        + "    @dec\n"
        + "    async def run(self):\n"
        + "        pass\n"
    )
    assert codigo == esperado


def test_clase_con_decorador_desde_parser():
    codigo_fuente = """@dec\nclase C:\n    pasar\nfin"""
    tokens = Lexer(codigo_fuente).analizar_token()
    ast = Parser(tokens).parsear()
    codigo = TranspiladorPython().generate_code(ast)
    esperado = IMPORTS + "@dec\nclass C:\n    pass\n"
    assert codigo == esperado


def test_imports_python_por_defecto():
    codigo = TranspiladorPython().generate_code([])
    assert codigo == IMPORTS


def test_transpilador_funcion_generica():
    func = NodoFuncion("identidad", ["x"], [NodoPasar()], type_params=["T"])
    codigo = TranspiladorPython().generate_code([func])
    esperado = (
        "from typing import TypeVar, Generic\n"
        + IMPORTS
        + "T = TypeVar('T')\n"
        + "def identidad(x):\n"
        + "    pass\n"
    )
    assert codigo == esperado


def test_transpilador_clase_generica():
    metodo = NodoMetodo("identidad", ["self", "x"], [NodoPasar()])
    clase = NodoClase("Caja", [metodo], type_params=["T"])
    codigo = TranspiladorPython().generate_code([clase])
    esperado = (
        "from typing import TypeVar, Generic\n"
        + IMPORTS
        + "T = TypeVar('T')\n"
        + "class Caja(Generic[T]):\n"
        + "    def identidad(self, x):\n"
        + "        pass\n"
    )
    assert codigo == esperado
