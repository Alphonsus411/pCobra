try:
    from pcobra.core.ast_nodes import (
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
        NodoPara,
        NodoWith,
        NodoDefer,
        NodoRetorno,
    )
    from pcobra.core.ast_nodes import NodoSwitch, NodoCase, NodoPattern, NodoGuard
except ImportError:  # pragma: no cover - compatibilidad
    from core.ast_nodes import (  # type: ignore
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
        NodoPara,
        NodoWith,
        NodoDefer,
        NodoRetorno,
    )
    from core.ast_nodes import (  # type: ignore
        NodoSwitch,
        NodoCase,
        NodoPattern,
        NodoGuard,
    )
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from pcobra.cobra.transpilers.transpiler.to_rust import TranspiladorRust
from pcobra.cobra.transpilers import import_helper as pc_import_helper
from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import Parser

get_standard_imports = pc_import_helper.get_standard_imports

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
        "import contextlib\n"
        + IMPORTS
        + "def miFuncion(a, b):\n"
        + "    with contextlib.ExitStack() as __cobra_defer_stack_0:\n"
        + "        x = a + b\n"
    )
    assert resultado == esperado


def test_transpilador_funcion_con_defer():
    ast = [
        NodoFuncion(
            "cerrar",
            [],
            [
                NodoDefer(NodoLlamadaFuncion("limpiar", []), linea=1, columna=1),
                NodoRetorno(NodoValor(1)),
            ],
        )
    ]
    transpilador = TranspiladorPython()
    resultado = transpilador.generate_code(ast)
    esperado = (
        "import contextlib\n"
        + IMPORTS
        + "def cerrar():\n"
        + "    with contextlib.ExitStack() as __cobra_defer_stack_0:\n"
        + "        __cobra_defer_stack_0.callback(lambda: limpiar())\n"
        + "        return 1\n"
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
        "import contextlib\n"
        + IMPORTS
        + "@d1\n"
        + "@d2\n"
        + "def saluda():\n"
        + "    with contextlib.ExitStack() as __cobra_defer_stack_0:\n"
        + "        print('hola')\n"
    )
    assert codigo == esperado


def test_alias_metodo_transpiladores_varios():
    codigo = """
    clase Coleccion:
        metodo iterar(self):
            pasar
        fin
    fin
    """
    tokens = Lexer(codigo).analizar_token()
    parser = Parser(tokens)
    ast = parser.parsear()
    clase = ast[0]
    metodo = clase.metodos[0]
    assert metodo.nombre == "__iter__"
    assert metodo.nombre_original == "iterar"
    assert parser.advertencias == []

    codigo_python = TranspiladorPython().generate_code(ast)
    assert "__iter__" in codigo_python

    codigo_js = TranspiladorJavaScript().generate_code(ast)
    assert "__iter__" in codigo_js

    codigo_rust = TranspiladorRust().generate_code(ast)
    assert "__iter__" in codigo_rust


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
        + "import contextlib\n"
        + IMPORTS
        + "async def saluda():\n"
        + "    with contextlib.ExitStack() as __cobra_defer_stack_0:\n"
        + "        print(1)\n"
        + "async def principal():\n"
        + "    with contextlib.ExitStack() as __cobra_defer_stack_1:\n"
        + "        await saluda()\n"
    )
    assert codigo == esperado


def test_transpilador_para_asincronico():
    bucle = NodoPara(
        "item",
        NodoIdentificador("datos"),
        [NodoPasar()],
        asincronico=True,
    )
    codigo = TranspiladorPython().generate_code([bucle])
    esperado = IMPORTS + "async for item in datos:\n    pass\n"
    assert codigo == esperado


def test_transpilador_with_asincronico():
    contexto = NodoWith(
        NodoIdentificador("recurso"),
        "alias",
        [NodoPasar()],
        asincronico=True,
    )
    codigo = TranspiladorPython().generate_code([contexto])
    esperado = IMPORTS + "async with recurso as alias:\n    pass\n"
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
        + "import contextlib\n"
        + IMPORTS
        + "class Hija(Base1, Base2):\n"
        + "    async def run(self):\n"
        + "        with contextlib.ExitStack() as __cobra_defer_stack_0:\n"
        + "            await tarea()\n"
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
        + "import contextlib\n"
        + IMPORTS
        + "@dec\n"
        + "class C:\n"
        + "    @dec\n"
        + "    async def run(self):\n"
        + "        with contextlib.ExitStack() as __cobra_defer_stack_0:\n"
        + "            pass\n"
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
        "import contextlib\n"
        + "from typing import TypeVar, Generic\n"
        + IMPORTS
        + "T = TypeVar('T')\n"
        + "def identidad(x):\n"
        + "    with contextlib.ExitStack() as __cobra_defer_stack_0:\n"
        + "        pass\n"
    )
    assert codigo == esperado


def test_transpilador_clase_generica():
    metodo = NodoMetodo("identidad", ["self", "x"], [NodoPasar()])
    clase = NodoClase("Caja", [metodo], type_params=["T"])
    codigo = TranspiladorPython().generate_code([clase])
    esperado = (
        "import contextlib\n"
        + "from typing import TypeVar, Generic\n"
        + IMPORTS
        + "T = TypeVar('T')\n"
        + "class Caja(Generic[T]):\n"
        + "    def identidad(self, x):\n"
        + "        with contextlib.ExitStack() as __cobra_defer_stack_0:\n"
        + "            pass\n"
    )
    assert codigo == esperado
