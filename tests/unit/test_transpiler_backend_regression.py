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
from pcobra.cobra.transpilers.common.utils import get_standard_imports
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
        ("go", "[]float64{1, 2, 3}"),
        ("java", "new double[]{1, 2, 3}"),
        ("wasm", ";; holobit hb [1, 2, 3]"),
        ("asm", "HOLOBIT hb [1, 2, 3]"),
    ],
)
def test_holobit_representative_generation(language: str, expected_snippet: str):
    transpiler = _build(language)
    code = transpiler.generate_code([NodoHolobit("hb", [1, 2, 3])])
    assert expected_snippet in _to_text(code)


@pytest.mark.parametrize(
    "language, expected",
    [
        ("python", "proyectar(hb"),
        ("js", "proyectar(hb"),
        ("rust", "cobra_proyectar"),
        ("go", "cobraProyectar"),
        ("cpp", "cobra_proyectar"),
        ("java", "cobraProyectar"),
        ("wasm", "cobra_proyectar"),
        ("asm", "NodoProyectar no soportado"),
    ],
)
def test_primitiva_proyectar_minima_por_backend(language: str, expected: str):
    transpiler = _build(language)
    code = transpiler.generate_code(
        [NodoHolobit("hb", [1, 2, 3]), NodoProyectar(NodoIdentificador("hb"), NodoValor("2d"))]
    )
    assert expected in _to_text(code)


@pytest.mark.parametrize("language", TRANSPILERS)
def test_primitiva_transformar_y_graficar_minima_por_backend(language: str):
    transpiler = _build(language)
    code = transpiler.generate_code(
        [
            NodoHolobit("hb", [1, 2, 3]),
            NodoTransformar(NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)]),
            NodoGraficar(NodoIdentificador("hb")),
        ]
    )
    text = _to_text(code)
    assert "hb" in text
    assert "grafic" in text.lower() or "graficar" in text.lower()


@pytest.mark.parametrize("language", ["python", "js", "rust", "wasm", "go", "cpp", "java", "asm"])
def test_operacion_libreria_runtime_representativa(language: str):
    transpiler = _build(language)
    code = transpiler.generate_code([NodoLlamadaFuncion("longitud", [NodoValor("cobra")])])
    text = _to_text(code)
    assert "longitud" in text


@pytest.mark.parametrize(
    "language, token_runtime",
    [
        ("python", "corelibs"),
        ("js", "nativos"),
        ("rust", "corelibs"),
        ("wasm", "runtime import"),
        ("go", "corelibs"),
        ("cpp", "corelibs"),
        ("java", "corelibs"),
        ("asm", "runtime import"),
    ],
)
def test_bootstrap_runtime_backend(language: str, token_runtime: str):
    imports = get_standard_imports(language)
    text = "\n".join(imports) if isinstance(imports, list) else imports
    assert token_runtime in text


def test_matriz_compatibilidad_cubre_todos_los_backends_oficiales():
    assert set(BACKEND_COMPATIBILITY) == set(TRANSPILERS)
