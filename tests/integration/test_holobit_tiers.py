from __future__ import annotations

import pytest

from pcobra.cobra.transpilers.registry import get_transpilers
from cobra.core import Lexer, Parser
from pcobra.cobra.transpilers.compatibility_matrix import (
    BACKEND_COMPATIBILITY,
    BACKEND_COMPATIBILITY_NOTES,
    BACKEND_FEATURE_GAPS,
    COMPATIBILITY_LEVEL_ORDER,
    CONTRACT_FEATURES,
    MIN_REQUIRED_BACKEND_COMPATIBILITY,
    SDK_FULL_BACKENDS,
    SDK_PARTIAL_BACKENDS,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from tests.utils.targets import assert_official_targets_partition, official_targets_for_tier

TRANSPILERS = get_transpilers()

HOLOBIT_CASES = {
    "holobit": "var h = holobit([1.0, 2.0, 3.0])\n",
    "graficar": 'var h = holobit([1.0, 2.0, 3.0])\ngraficar(h)\n',
    "proyectar": 'var h = holobit([1.0, 2.0, 3.0])\nproyectar(h, "2D")\n',
    "transformar": 'var h = holobit([1.0, 2.0, 3.0])\ntransformar(h, "rotar", "z", 45)\n',
}
PYTHON_RUNTIME_ONLY_CASES = {
    "escalar": 'var h = holobit([1.0, 2.0, 3.0])\nescalar(h, 2)\n',
    "mover": 'var h = holobit([1.0, 2.0, 3.0])\nmover(h, 1, 2, 3)\n',
}
SUPPORTED_BY_TIER = {
    tier: {primitive: official_targets_for_tier(tier) for primitive in HOLOBIT_CASES}
    for tier in ("tier1", "tier2")
}
PARTIAL_MARKERS = {
    "javascript": {
        "holobit": ("__cobra_tipo__: 'holobit'",),
        "proyectar": ("case '2d':",),
        "transformar": ("operacion === 'rotar'",),
        "graficar": ("const vista = `Holobit(${holobit.valores.join(', ')})`;",),
    },
    "rust": {
        "holobit": ("struct CobraHolobit",),
        "proyectar": ("fn cobra_proyectar",),
        "transformar": ("fn cobra_transformar", "if eje != \"z\" {"),
        "graficar": ("fn cobra_graficar",),
    },
    "wasm": {
        "holobit": ('(import "pcobra:holobit" "cobra_holobit"',),
        "proyectar": ("(func $cobra_proyectar",),
        "transformar": ("(func $cobra_transformar",),
        "graficar": ("(func $cobra_graficar",),
    },
    "go": {"holobit": ("cobra_holobit([]float64{1.0, 2.0, 3.0})",), "proyectar": ("func cobra_proyectar",), "transformar": ("func cobra_transformar",), "graficar": ("func cobra_graficar",)},
    "cpp": {"holobit": ("cobra_holobit({ 1.0, 2.0, 3.0 });",), "proyectar": ("inline std::vector<double> cobra_proyectar",), "transformar": ("inline CobraHolobit cobra_transformar",), "graficar": ("inline std::string cobra_graficar",)},
    "java": {"holobit": ("cobra_holobit(new double[]{1.0, 2.0, 3.0});",), "proyectar": ("private static double[] cobra_proyectar",), "transformar": ("private static CobraHolobit cobra_transformar",), "graficar": ("private static String cobra_graficar",)},
    "asm": {"holobit": ("cobra_holobit:",), "proyectar": ("cobra_proyectar:",), "transformar": ("cobra_transformar:",), "graficar": ("cobra_graficar:",)},
}
FULL_MARKERS = {
    "python": {
        "holobit": ("from corelibs import *", "cobra_holobit([1.0, 2.0, 3.0])"),
        "proyectar": ("def cobra_proyectar", "cobra_proyectar(h"),
        "transformar": ("def cobra_transformar", "cobra_transformar(h"),
        "graficar": ("def cobra_graficar", "cobra_graficar(h"),
    }
}
RUNTIME_SMOKE_MARKERS = {
    "python": {"corelibs": ("from corelibs import *", "longitud('cobra')"), "standard_library": ("from standard_library import *", "mostrar('hola')")},
    "javascript": {"corelibs": ("const longitud = (valor) => cobraJsCorelibs.longitud(valor);", "longitud('cobra');"), "standard_library": ("const mostrar = (...args) => cobraJsStandardLibrary.mostrar(...args);", "mostrar('hola');")},
    "rust": {"corelibs": ('fn longitud<T: ToString>(valor: T) -> usize {', 'longitud("cobra");'), "standard_library": ('fn mostrar<T: Display>(valor: T) {', 'mostrar("hola");')},
    "wasm": {"corelibs": ('(import "pcobra:corelibs" "longitud"', '(call $longitud (i32.const 0))'), "standard_library": ('(import "pcobra:standard_library" "mostrar"', '(call $mostrar (i32.const 0))')},
    "go": {"corelibs": ('"pcobra/corelibs"', 'longitud("cobra")'), "standard_library": ('"pcobra/standard_library"', 'mostrar("hola")')},
    "cpp": {"corelibs": ("#include <pcobra/corelibs.hpp>", 'longitud("cobra");'), "standard_library": ("#include <pcobra/standard_library.hpp>", 'mostrar("hola");')},
    "java": {"corelibs": ("import pcobra.corelibs.*;", 'longitud("cobra")'), "standard_library": ("import pcobra.standard_library.*;", 'mostrar("hola")')},
    "asm": {"corelibs": ("CALL longitud 'cobra'",), "standard_library": ("CALL mostrar 'hola'",)},
}
HOOK_MARKERS = {
    "python": ("def cobra_holobit", "def cobra_proyectar", "def cobra_transformar", "def cobra_graficar"),
    "javascript": ("function cobra_holobit", "function cobra_proyectar", "function cobra_transformar", "function cobra_graficar"),
    "rust": ("fn cobra_holobit", "fn cobra_proyectar", "fn cobra_transformar", "fn cobra_graficar"),
    "wasm": ("(func $cobra_holobit", "(func $cobra_proyectar", "(func $cobra_transformar", "(func $cobra_graficar"),
    "go": ("func cobra_holobit", "func cobra_proyectar", "func cobra_transformar", "func cobra_graficar"),
    "cpp": ("inline CobraHolobit cobra_holobit", "inline std::vector<double> cobra_proyectar", "inline CobraHolobit cobra_transformar", "inline std::string cobra_graficar"),
    "java": ("private static CobraHolobit cobra_holobit", "private static double[] cobra_proyectar", "private static CobraHolobit cobra_transformar", "private static String cobra_graficar"),
    "asm": ("cobra_holobit:", "cobra_proyectar:", "cobra_transformar:", "cobra_graficar:"),
}
CONTRACTUAL_ERROR_MARKERS = {
    "python": ("Runtime Holobit Python:", "holobit_sdk"),
    "javascript": ("Runtime Holobit JavaScript:", "contrato partial", "holobit_sdk"),
    "rust": ("Runtime Holobit Rust:", "contrato partial", "holobit_sdk"),
    "wasm": ("Runtime Holobit Wasm:", "contrato partial", "host-managed"),
    "go": ("Runtime Holobit Go:", "contrato partial", "holobit_sdk"),
    "cpp": ("Runtime Holobit C++:", "contrato partial", "holobit_sdk"),
    "java": ("Runtime Holobit Java:", "contrato partial", "holobit_sdk"),
    "asm": ("contrato partial", "sin holobit_sdk", "TRAP"),
}


def _transpilar(codigo: str, lang: str) -> str:
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    salida = TRANSPILERS[lang]().generate_code(ast)
    return "\n".join(salida) if isinstance(salida, list) else str(salida)


def _assert_minimum_compatibility(backend: str, feature: str):
    actual = BACKEND_COMPATIBILITY[backend][feature]
    required = MIN_REQUIRED_BACKEND_COMPATIBILITY[backend][feature]
    assert COMPATIBILITY_LEVEL_ORDER[actual] >= COMPATIBILITY_LEVEL_ORDER[required]


def test_particion_oficial_de_tiers_permanece_como_fuente_unica():
    partition = assert_official_targets_partition(transpilers=TRANSPILERS)
    assert tuple(partition) == ("tier1", "tier2")



@pytest.mark.parametrize("tier", ["tier1", "tier2"])
@pytest.mark.parametrize("caso", HOLOBIT_CASES.keys())
def test_holobit_cobertura_por_tier(tier, caso):
    codigo = HOLOBIT_CASES[caso]
    langs = SUPPORTED_BY_TIER[tier][caso]
    for lang in langs:
        salida = _transpilar(codigo, lang)
        assert salida.strip()
        if lang == "python":
            for marker in FULL_MARKERS[lang][caso]:
                assert marker in salida
        else:
            for marker in PARTIAL_MARKERS[lang][caso]:
                assert marker in salida


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_matriz_compatibilidad_respeta_minimo_contractual_por_backend(backend):
    assert BACKEND_COMPATIBILITY[backend]["tier"] == MIN_REQUIRED_BACKEND_COMPATIBILITY[backend]["tier"]
    for feature in ("holobit", "proyectar", "transformar", "graficar", "corelibs", "standard_library"):
        _assert_minimum_compatibility(backend, feature)


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
@pytest.mark.parametrize("runtime_feature", ("corelibs", "standard_library"))
def test_runtime_import_smoke_por_backend(backend, runtime_feature):
    salida = _transpilar("longitud(\"cobra\")\n" if runtime_feature == "corelibs" else "mostrar(\"hola\")\n", backend)
    for marker in RUNTIME_SMOKE_MARKERS[backend][runtime_feature]:
        assert marker in salida


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_runtime_hooks_cobra_smoke_por_backend(backend):
    salida = _transpilar(HOLOBIT_CASES["graficar"], backend)
    for marker in HOOK_MARKERS[backend]:
        assert marker in salida


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_runtime_hooks_incluyen_mensajes_contractuales_por_backend(backend):
    salida = _transpilar(HOLOBIT_CASES["transformar"], backend)
    for marker in CONTRACTUAL_ERROR_MARKERS[backend]:
        assert marker in salida


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
@pytest.mark.parametrize("feature", ("holobit", "proyectar", "transformar", "graficar"))
def test_hooks_runtime_respetan_nivel_full_partial_de_matriz(backend: str, feature: str):
    salida = _transpilar(HOLOBIT_CASES[feature], backend)
    level = BACKEND_COMPATIBILITY[backend][feature]
    assert level in {"full", "partial"}
    if level == "full":
        assert backend == "python"
        assert "Runtime Holobit Python:" in salida
    else:
        assert "partial" in salida.lower()
        if backend == "wasm":
            assert "host-managed" in salida
        elif backend == "asm":
            assert "TRAP" in salida
        else:
            assert "holobit_sdk" in salida


def test_only_python_es_full_para_holobit_y_runtime_base():
    assert SDK_FULL_BACKENDS == ("python",)
    assert set(SDK_FULL_BACKENDS).isdisjoint(SDK_PARTIAL_BACKENDS)
    assert set(SDK_PARTIAL_BACKENDS) == set(OFFICIAL_TARGETS) - {"python"}
    for feature in CONTRACT_FEATURES:
        full_backends = {backend for backend in OFFICIAL_TARGETS if BACKEND_COMPATIBILITY[backend][feature] == "full"}
        partial_backends = {backend for backend in OFFICIAL_TARGETS if BACKEND_COMPATIBILITY[backend][feature] == "partial"}
        assert full_backends == {"python"}
        assert partial_backends == set(SDK_PARTIAL_BACKENDS)


def test_sdk_full_y_partial_se_mantienen_como_particion_exacta_de_official_targets():
    full = set(SDK_FULL_BACKENDS)
    partial = set(SDK_PARTIAL_BACKENDS)
    official = set(OFFICIAL_TARGETS)
    assert full & partial == set()
    assert full | partial == official


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_backends_partial_declaran_gaps_explicitos_por_feature(backend):
    for feature in CONTRACT_FEATURES:
        level = BACKEND_COMPATIBILITY[backend][feature]
        gaps = BACKEND_FEATURE_GAPS[backend][feature]
        if level == "full":
            assert gaps == ()
        elif level == "partial":
            assert len(gaps) >= 1


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_backends_declaran_notas_explicitas_y_trazables(backend):
    notes = BACKEND_COMPATIBILITY_NOTES[backend]
    assert notes["contract"] == ("full" if backend in SDK_FULL_BACKENDS else "partial")
    assert isinstance(notes["evidence"], str)
    assert notes["evidence"].strip()


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
@pytest.mark.parametrize("caso", PYTHON_RUNTIME_ONLY_CASES.keys())
def test_escalar_y_mover_se_preservan_como_llamadas_pero_no_se_tratan_como_contrato(backend, caso):
    salida = _transpilar(PYTHON_RUNTIME_ONLY_CASES[caso], backend)
    assert salida.strip()
