import pytest

from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoGraficar,
    NodoHolobit,
    NodoIdentificador,
    NodoProyectar,
    NodoTransformar,
    NodoValor,
)
from pcobra.cobra.transpilers.transpiler.to_asm import TranspiladorASM
from pcobra.cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from pcobra.cobra.transpilers.transpiler.to_go import TranspiladorGo
from pcobra.cobra.transpilers.transpiler.to_java import TranspiladorJava
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.transpiler.to_rust import TranspiladorRust
from pcobra.cobra.transpilers.transpiler.to_wasm import TranspiladorWasm


RUNTIME_MARKERS = [
    (TranspiladorPython, "def cobra_proyectar("),
    (TranspiladorJavaScript, "function cobra_proyectar("),
    (TranspiladorRust, "fn cobra_proyectar("),
    (TranspiladorWasm, "(func $cobra_proyectar"),
    (TranspiladorGo, "func cobraProyectar("),
    (TranspiladorCPP, "inline void cobra_proyectar("),
    (TranspiladorJava, "private static void cobraProyectar("),
    (TranspiladorASM, "cobra_proyectar:"),
]


def _programa_holobit_minimo():
    hb = NodoIdentificador("hb")
    return [
        NodoHolobit(nombre="hb", valores=[1.0, 2.0, 3.0]),
        NodoProyectar(holobit=hb, modo=NodoValor("2d")),
        NodoTransformar(
            holobit=hb,
            operacion=NodoValor("rotar"),
            parametros=[NodoValor(90)],
        ),
        NodoGraficar(holobit=hb),
    ]


def _programa_sin_holobit():
    return [NodoAsignacion(variable="x", expresion=NodoValor(1))]


@pytest.mark.parametrize(("transpilador_cls", "runtime_marker"), RUNTIME_MARKERS)
def test_inserta_runtime_hooks_con_nodos_holobit(transpilador_cls, runtime_marker):
    codigo = transpilador_cls().generate_code(_programa_holobit_minimo())
    assert runtime_marker in codigo


@pytest.mark.parametrize(("transpilador_cls", "runtime_marker"), RUNTIME_MARKERS)
def test_no_inserta_runtime_hooks_sin_nodos_holobit(transpilador_cls, runtime_marker):
    codigo = transpilador_cls().generate_code(_programa_sin_holobit())
    assert runtime_marker not in codigo
