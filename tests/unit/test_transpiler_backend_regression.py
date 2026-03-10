import importlib

import pytest

from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoGraficar,
    NodoHolobit,
    NodoIdentificador,
    NodoLlamadaFuncion,
    NodoProyectar,
    NodoTransformar,
    NodoValor,
)
from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY

TRANSPILERS = {
    "python": ("pcobra.cobra.transpilers.transpiler.to_python", "TranspiladorPython"),
    "js": ("pcobra.cobra.transpilers.transpiler.to_js", "TranspiladorJavaScript"),
    "rust": ("pcobra.cobra.transpilers.transpiler.to_rust", "TranspiladorRust"),
    "wasm": ("pcobra.cobra.transpilers.transpiler.to_wasm", "TranspiladorWasm"),
    "go": ("pcobra.cobra.transpilers.transpiler.to_go", "TranspiladorGo"),
    "cpp": ("pcobra.cobra.transpilers.transpiler.to_cpp", "TranspiladorCPP"),
    "java": ("pcobra.cobra.transpilers.transpiler.to_java", "TranspiladorJava"),
    "asm": ("pcobra.cobra.transpilers.transpiler.to_asm", "TranspiladorASM"),
}


def _build(language: str):
    mod_name, cls_name = TRANSPILERS[language]
    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)()


def _to_text(output) -> str:
    return "\n".join(output) if isinstance(output, list) else str(output)


@pytest.mark.parametrize("language", TRANSPILERS)
def test_import_backend_module_and_generate_minimal_code(language: str):
    """Smoke test de imports + generación mínima para evitar roturas por dependencias."""
    transpiler = _build(language)
    code = transpiler.generate_code([NodoAsignacion("x", NodoValor(1))])
    text = _to_text(code)
    assert text.strip()


@pytest.mark.parametrize(
    "language, expected_snippet",
    [
        ("python", "holobit([1, 2, 3])"),
        ("js", "new Holobit([1, 2, 3])"),
        ("rust", "holobit(vec![1, 2, 3])"),
        ("cpp", "holobit({ 1, 2, 3 })"),
        ("asm", "HOLOBIT hb [1, 2, 3]"),
    ],
)
def test_holobit_representative_generation(language: str, expected_snippet: str):
    transpiler = _build(language)
    code = transpiler.generate_code([NodoHolobit("hb", [1, 2, 3])])
    assert expected_snippet in _to_text(code)


@pytest.mark.parametrize(
    "language,node_cls,args",
    [
        ("python", NodoProyectar, (NodoIdentificador("hb"), NodoValor("2d"))),
        ("python", NodoTransformar, (NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)])),
        ("python", NodoGraficar, (NodoIdentificador("hb"),)),
        ("js", NodoProyectar, (NodoIdentificador("hb"), NodoValor("2d"))),
        ("js", NodoTransformar, (NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)])),
        ("js", NodoGraficar, (NodoIdentificador("hb"),)),
    ],
)
def test_primitivas_holobit_tier1_full(language, node_cls, args):
    transpiler = _build(language)
    code = transpiler.generate_code([NodoHolobit("hb", [1, 2, 3]), node_cls(*args)])
    text = _to_text(code)
    assert "hb" in text


@pytest.mark.parametrize("language", ["rust", "cpp", "java"])
def test_primitivas_holobit_limitadas_lanzan_not_implemented(language: str):
    transpiler = _build(language)
    with pytest.raises(NotImplementedError):
        transpiler.generate_code([NodoProyectar(NodoIdentificador("hb"), NodoValor("2d"))])


@pytest.mark.parametrize("language", ["python", "js", "rust", "go", "cpp", "java", "asm"])
def test_operacion_libreria_runtime_representativa(language: str):
    """Representa una operación típica de librerías usadas en runtime."""
    transpiler = _build(language)
    code = transpiler.generate_code([NodoLlamadaFuncion("longitud", [NodoValor("cobra")])])
    text = _to_text(code)
    assert "longitud" in text


def test_matriz_compatibilidad_cubre_todos_los_backends_oficiales():
    assert set(BACKEND_COMPATIBILITY) == set(TRANSPILERS)
