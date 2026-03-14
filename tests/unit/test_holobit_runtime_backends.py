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
from pcobra.cobra.transpilers.common.utils import get_runtime_hooks, get_standard_imports
from pcobra.cobra.transpilers.transpiler.to_asm import TranspiladorASM
from pcobra.cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from pcobra.cobra.transpilers.transpiler.to_go import TranspiladorGo
from pcobra.cobra.transpilers.transpiler.to_java import TranspiladorJava
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.transpiler.to_rust import TranspiladorRust
from pcobra.cobra.transpilers.transpiler.to_wasm import TranspiladorWasm


BACKENDS = [
    ("python", TranspiladorPython),
    ("javascript", TranspiladorJavaScript),
    ("rust", TranspiladorRust),
    ("wasm", TranspiladorWasm),
    ("go", TranspiladorGo),
    ("cpp", TranspiladorCPP),
    ("java", TranspiladorJava),
    ("asm", TranspiladorASM),
]

HOOK_SYMBOLS = {
    "python": ["cobra_holobit(", "cobra_proyectar(", "cobra_transformar(", "cobra_graficar("],
    "javascript": ["cobra_holobit(", "cobra_proyectar(", "cobra_transformar(", "cobra_graficar("],
    "rust": ["cobra_holobit(", "cobra_proyectar(", "cobra_transformar(", "cobra_graficar("],
    "wasm": ["$cobra_holobit", "$cobra_proyectar", "$cobra_transformar", "$cobra_graficar"],
    "go": ["cobraHolobit(", "cobraProyectar(", "cobraTransformar(", "cobraGraficar("],
    "cpp": ["cobra_holobit(", "cobra_proyectar(", "cobra_transformar(", "cobra_graficar("],
    "java": ["cobraHolobit(", "cobraProyectar(", "cobraTransformar(", "cobraGraficar("],
    "asm": ["cobra_holobit:", "cobra_proyectar:", "cobra_transformar:", "cobra_graficar:"],
}


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


@pytest.mark.parametrize(("target", "transpilador_cls"), BACKENDS)
def test_inserta_hooks_runtime_holobit_desde_contrato_central(target, transpilador_cls):
    codigo = transpilador_cls().generate_code(_programa_holobit_minimo())

    # contrato central: al usar Holobit, todos los hooks del backend deben aparecer
    for marcador in HOOK_SYMBOLS[target]:
        assert marcador in codigo

    for linea in get_runtime_hooks(target):
        if linea.strip():
            assert linea in codigo


@pytest.mark.parametrize(("target", "transpilador_cls"), BACKENDS)
def test_no_inserta_runtime_hooks_sin_nodos_holobit(target, transpilador_cls):
    codigo = transpilador_cls().generate_code(_programa_sin_holobit())
    for marcador in HOOK_SYMBOLS[target]:
        assert marcador not in codigo


@pytest.mark.parametrize(("target", "transpilador_cls"), BACKENDS)
def test_imports_minimos_runtime_por_backend(target, transpilador_cls):
    codigo = transpilador_cls().generate_code(_programa_holobit_minimo())
    imports = get_standard_imports(target)
    if isinstance(imports, str):
        imports = [line for line in imports.splitlines() if line.strip()]
    for linea in imports:
        assert linea in codigo
