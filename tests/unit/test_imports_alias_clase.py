from backend.src.core.ast_nodes import (
    NodoImportDesde,
    NodoDecorador,
    NodoClase,
    NodoMetodo,
    NodoEsperar,
    NodoLlamadaFuncion,
    NodoIdentificador,
)
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from src.cobra.transpilers.import_helper import get_standard_imports

IMPORTS_PY = get_standard_imports("python")


def crear_ast():
    imports = [
        NodoImportDesde("package.module", "decorador", "dec"),
        NodoImportDesde("package2.module2", "Base", "B"),
    ]
    metodo = NodoMetodo(
        "run",
        ["self"],
        [NodoEsperar(NodoLlamadaFuncion("accion", []))],
        asincronica=True,
    )
    metodo.decoradores = [NodoDecorador(NodoIdentificador("dec"))]
    clase = NodoClase("C", [metodo], ["B"])
    clase.decoradores = [NodoDecorador(NodoIdentificador("dec"))]
    return imports + [clase]


def test_transpilador_python_imports_alias_clase():
    ast = crear_ast()
    resultado = TranspiladorPython().generate_code(ast)
    esperado = (
        "import asyncio\n"
        + IMPORTS_PY
        + "from package.module import decorador as dec\n"
        "from package2.module2 import Base as B\n"
        "@dec\n"
        "class C(B):\n"
        "    @dec\n"
        "    async def run(self):\n"
        "        await accion()\n"
    )
    assert resultado == esperado


IMPORTS = (
    "import * as io from './nativos/io.js';\n"
    "import * as net from './nativos/io.js';\n"
    "import * as matematicas from './nativos/matematicas.js';\n"
    "import { Pila, Cola } from './nativos/estructuras.js';\n"
)


def test_transpilador_js_imports_alias_clase():
    ast = crear_ast()
    resultado = TranspiladorJavaScript().generate_code(ast)
    esperado = IMPORTS + (
        "import { decorador as dec } from 'package.module';\n"
        "import { Base as B } from 'package2.module2';\n"
        "class C extends B {\n"
        "async run(self) {\n"
        "await accion();\n"
        "}\n"
        "}\n"
        "C.prototype.run = dec(C.prototype.run);\n"
        "C = dec(C);"
    )
    assert resultado == esperado
