import pytest

from cobra.cli.commands.compile_cmd import TRANSPILERS
from cobra.core import Lexer, Parser
from pcobra.cobra.transpilers.compatibility_matrix import (
    BACKEND_COMPATIBILITY,
    COMPATIBILITY_LEVEL_ORDER,
    CONTRACT_FEATURES,
    MIN_REQUIRED_BACKEND_COMPATIBILITY,
    SDK_FULL_BACKENDS,
    SDK_PARTIAL_BACKENDS,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS

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
    "tier1": {primitive: TIER1_TARGETS for primitive in HOLOBIT_CASES},
    "tier2": {primitive: TIER2_TARGETS for primitive in HOLOBIT_CASES},
}

# Contrato explícito por primitive/backend para distinguir asserts full vs partial.
PRIMITIVE_CONTRACT = {
    "holobit": {
        "full": ("python",),
        "partial": ("javascript", "rust", "wasm", "go", "cpp", "java", "asm"),
    },
    "proyectar": {
        "full": ("python",),
        "partial": ("javascript", "rust", "wasm", "go", "cpp", "java", "asm"),
    },
    "transformar": {
        "full": ("python",),
        "partial": ("javascript", "rust", "wasm", "go", "cpp", "java", "asm"),
    },
    "graficar": {
        "full": ("python",),
        "partial": ("javascript", "rust", "wasm", "go", "cpp", "java", "asm"),
    },
}


PARTIAL_ADVANCED_FAILURE_PRIMITIVES = {
    "javascript": {"proyectar": "throw new Error", "transformar": "throw new Error", "graficar": "throw new Error"},
    "rust": {"proyectar": "panic!(", "transformar": "panic!(", "graficar": "panic!("},
    "wasm": {"proyectar": "unreachable", "transformar": "unreachable", "graficar": "unreachable"},
    "go": {"proyectar": "panic(fmt.Sprintf", "transformar": "panic(fmt.Sprintf", "graficar": "panic(fmt.Sprintf"},
    "cpp": {"proyectar": "throw std::runtime_error", "transformar": "throw std::runtime_error", "graficar": "throw std::runtime_error"},
    "java": {"proyectar": "throw new UnsupportedOperationException", "transformar": "throw new UnsupportedOperationException", "graficar": "throw new UnsupportedOperationException"},
    "asm": {"proyectar": "TRAP", "transformar": "TRAP", "graficar": "TRAP"},
}
FULL_EXPECTATIONS = {
    "python": {
        "holobit": ("from corelibs import *", "from standard_library import *", "cobra_holobit([1.0, 2.0, 3.0])"),
        "proyectar": ("def cobra_proyectar", "cobra_proyectar(h"),
        "transformar": ("def cobra_transformar", "cobra_transformar(h"),
        "graficar": ("def cobra_graficar", "cobra_graficar(h"),
    },
}

PARTIAL_FALLBACK_MARKERS = {
    "javascript": {
        "holobit": ("function cobra_holobit", "let h ="),
        "proyectar": ("function cobra_proyectar", "Runtime Holobit JavaScript: 'proyectar' requiere runtime avanzado compatible."),
        "transformar": ("function cobra_transformar", "Runtime Holobit JavaScript: 'transformar' requiere runtime avanzado compatible."),
        "graficar": ("function cobra_graficar", "Runtime Holobit JavaScript: 'graficar' requiere runtime avanzado compatible."),
    },
    "rust": {
        "holobit": ("cobra_holobit(vec![1.0, 2.0, 3.0]);",),
        "proyectar": ("fn cobra_proyectar",),
        "transformar": ("fn cobra_transformar",),
        "graficar": ("fn cobra_graficar",),
    },
    "wasm": {
        "holobit": ("(func $cobra_holobit", "(local.set $h (call $cobra_holobit"),
        "proyectar": ("(func $cobra_proyectar",),
        "transformar": ("(func $cobra_transformar",),
        "graficar": ("(func $cobra_graficar",),
    },
    "go": {
        "holobit": ("cobra_holobit([]float64{1.0, 2.0, 3.0})",),
        "proyectar": ("func cobra_proyectar",),
        "transformar": ("func cobra_transformar",),
        "graficar": ("func cobra_graficar",),
    },
    "cpp": {
        "holobit": ("cobra_holobit({ 1.0, 2.0, 3.0 });",),
        "proyectar": ("inline void cobra_proyectar",),
        "transformar": ("inline void cobra_transformar",),
        "graficar": ("inline void cobra_graficar",),
    },
    "java": {
        "holobit": ("cobra_holobit(new double[]{1.0, 2.0, 3.0});",),
        "proyectar": ("private static void cobra_proyectar",),
        "transformar": ("private static void cobra_transformar",),
        "graficar": ("private static void cobra_graficar",),
    },
    "asm": {
        "holobit": ("cobra_holobit:", "SET h, cobra_holobit([1.0, 2.0, 3.0])"),
        "proyectar": ("cobra_proyectar:", "CALL cobra_proyectar h, '2D'"),
        "transformar": ("cobra_transformar:", "CALL cobra_transformar h, 'rotar', 'z', 45"),
        "graficar": ("cobra_graficar:", "CALL cobra_graficar h"),
    },
}



def _transpilar(codigo: str, lang: str) -> str:
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    salida = TRANSPILERS[lang]().generate_code(ast)
    return "\n".join(salida) if isinstance(salida, list) else str(salida)


def _assert_full_or_partial_contract(lang: str, caso: str, salida: str):
    if lang in PRIMITIVE_CONTRACT[caso]["full"]:
        strict_symbols = FULL_EXPECTATIONS[lang][caso]
        for symbol in strict_symbols:
            assert symbol in salida
        return

    if lang in PRIMITIVE_CONTRACT[caso]["partial"]:
        fallback_markers = PARTIAL_FALLBACK_MARKERS[lang][caso]
        for marker in fallback_markers:
            assert marker in salida
        assert salida.strip(), f"{lang} debe generar salida no vacía para {caso}"
        return

    if lang in PRIMITIVE_CONTRACT[caso].get("none", ()):
        pytest.fail(
            f"Backend {lang} no debe llegar a asserts de salida para primitive {caso}"
        )

    pytest.fail(f"Backend {lang} no clasificado en contrato para primitive {caso}")


@pytest.mark.parametrize("tier", ["tier1", "tier2"])
@pytest.mark.parametrize("caso", HOLOBIT_CASES.keys())
def test_holobit_cobertura_por_tier(tier, caso):
    codigo = HOLOBIT_CASES[caso]
    langs = SUPPORTED_BY_TIER[tier][caso]
    assert langs, f"El caso {caso} debe tener al menos un backend en {tier}"

    for lang in langs:
        if caso in BACKEND_COMPATIBILITY[lang] and BACKEND_COMPATIBILITY[lang][caso] == "none":
            with pytest.raises(NotImplementedError):
                _transpilar(codigo, lang)
            continue

        salida = _transpilar(codigo, lang)
        assert isinstance(salida, str)
        assert salida.strip()
        _assert_full_or_partial_contract(lang, caso, salida)


MIN_CONTRACT_FEATURES = ("holobit", "proyectar", "transformar", "graficar", "corelibs", "standard_library")
RUNTIME_CASES = {
    "corelibs": "longitud(\"cobra\")\n",
    "standard_library": "mostrar(\"hola\")\n",
}
RUNTIME_SMOKE_MARKERS = {
    "python": {
        "corelibs": ("from corelibs import *", "longitud('cobra')"),
        "standard_library": ("from standard_library import *", "mostrar('hola')"),
    },
    "javascript": {
        "corelibs": ("import * as texto from './nativos/texto.js';", "longitud('cobra');"),
        "standard_library": ("import * as io from './nativos/io.js';", "mostrar('hola');"),
    },
    "rust": {
        "corelibs": ("use crate::corelibs::*;", 'longitud("cobra");'),
        "standard_library": ("use crate::standard_library::*;", 'mostrar("hola");'),
    },
    "wasm": {
        "corelibs": (";; backend wasm: imports de runtime administrados externamente", "(call $longitud (i32.const 0))"),
        "standard_library": (";; backend wasm: imports de runtime administrados externamente", "(call $mostrar (i32.const 0))"),
    },
    "go": {
        "corelibs": ('"cobra/corelibs"', 'longitud("cobra")'),
        "standard_library": ('"cobra/standard_library"', 'mostrar("hola")'),
    },
    "cpp": {
        "corelibs": ("#include <cobra/corelibs.hpp>", 'longitud("cobra");'),
        "standard_library": ("#include <cobra/standard_library.hpp>", 'mostrar("hola");'),
    },
    "java": {
        "corelibs": ("import cobra.corelibs.*;", 'longitud("cobra")'),
        "standard_library": ("import cobra.standard_library.*;", 'mostrar("hola")'),
    },
    "asm": {
        "corelibs": ("CALL longitud 'cobra'",),
        "standard_library": ("CALL mostrar 'hola'",),
    },
}
HOLOBIT_HOOK_MARKERS = {
    "python": ("def cobra_holobit", "def cobra_proyectar", "def cobra_transformar", "def cobra_graficar"),
    "javascript": ("function cobra_holobit", "function cobra_proyectar", "function cobra_transformar", "function cobra_graficar"),
    "rust": ("fn cobra_holobit", "fn cobra_proyectar", "fn cobra_transformar", "fn cobra_graficar"),
    "wasm": ("(func $cobra_holobit", "(func $cobra_proyectar", "(func $cobra_transformar", "(func $cobra_graficar"),
    "go": ("func cobra_holobit", "func cobra_proyectar", "func cobra_transformar", "func cobra_graficar"),
    "cpp": ("inline auto cobra_holobit", "inline void cobra_proyectar", "inline void cobra_transformar", "inline void cobra_graficar"),
    "java": ("private static Object cobra_holobit", "private static void cobra_proyectar", "private static void cobra_transformar", "private static void cobra_graficar"),
    "asm": ("cobra_holobit:", "cobra_proyectar:", "cobra_transformar:", "cobra_graficar:"),
}


def _assert_minimum_compatibility(backend: str, feature: str):
    actual = BACKEND_COMPATIBILITY[backend][feature]
    required = MIN_REQUIRED_BACKEND_COMPATIBILITY[backend][feature]
    assert COMPATIBILITY_LEVEL_ORDER[actual] >= COMPATIBILITY_LEVEL_ORDER[required], (
        f"Regresión contractual: {backend}.{feature}={actual} < mínimo requerido {required}"
    )


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_matriz_compatibilidad_respeta_minimo_contractual_por_backend(backend):
    assert BACKEND_COMPATIBILITY[backend]["tier"] == MIN_REQUIRED_BACKEND_COMPATIBILITY[backend]["tier"]
    for feature in MIN_CONTRACT_FEATURES:
        _assert_minimum_compatibility(backend, feature)


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
@pytest.mark.parametrize("runtime_feature", ("corelibs", "standard_library"))
def test_runtime_import_smoke_por_backend(backend, runtime_feature):
    _assert_minimum_compatibility(backend, runtime_feature)
    salida = _transpilar(RUNTIME_CASES[runtime_feature], backend)
    assert salida.strip(), f"{backend} debe generar salida no vacía para {runtime_feature}"

    for marker in RUNTIME_SMOKE_MARKERS[backend][runtime_feature]:
        assert marker in salida


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_runtime_hooks_cobra_smoke_por_backend(backend):
    salida = _transpilar(HOLOBIT_CASES["graficar"], backend)
    assert salida.strip(), f"{backend} debe generar salida no vacía para hooks cobra_*"

    for hook_marker in HOLOBIT_HOOK_MARKERS[backend]:
        assert hook_marker in salida


def test_only_python_es_full_para_holobit_y_runtime_base():
    assert SDK_FULL_BACKENDS == ("python",)
    assert set(SDK_PARTIAL_BACKENDS) == set(OFFICIAL_TARGETS) - {"python"}

    for feature in CONTRACT_FEATURES:
        full_backends = {
            backend
            for backend in OFFICIAL_TARGETS
            if BACKEND_COMPATIBILITY[backend][feature] == "full"
        }
        partial_backends = {
            backend
            for backend in OFFICIAL_TARGETS
            if BACKEND_COMPATIBILITY[backend][feature] == "partial"
        }
        assert full_backends == {"python"}
        assert partial_backends == set(SDK_PARTIAL_BACKENDS)


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
@pytest.mark.parametrize("caso", PYTHON_RUNTIME_ONLY_CASES.keys())
def test_escalar_y_mover_se_preservan_como_llamadas_pero_no_se_tratan_como_contrato(backend, caso):
    salida = _transpilar(PYTHON_RUNTIME_ONLY_CASES[caso], backend)
    assert salida.strip()

    expected_markers = {
        "python": {
            "escalar": "escalar(h, 2)",
            "mover": "mover(h, 1, 2, 3)",
        },
        "javascript": {
            "escalar": "escalar(h, 2);",
            "mover": "mover(h, 1, 2, 3);",
        },
        "rust": {
            "escalar": "escalar(h, 2);",
            "mover": "mover(h, 1, 2, 3);",
        },
        "wasm": {
            "escalar": "(call $escalar",
            "mover": "(call $mover",
        },
        "go": {
            "escalar": "escalar(h, 2)",
            "mover": "mover(h, 1, 2, 3)",
        },
        "cpp": {
            "escalar": "escalar(h, 2);",
            "mover": "mover(h, 1, 2, 3);",
        },
        "java": {
            "escalar": "escalar(h, 2);",
            "mover": "mover(h, 1, 2, 3);",
        },
        "asm": {
            "escalar": "CALL escalar h, 2",
            "mover": "CALL mover h, 1, 2, 3",
        },
    }

    assert expected_markers[backend][caso] in salida


@pytest.mark.parametrize("backend", SDK_PARTIAL_BACKENDS)
@pytest.mark.parametrize("feature", ("proyectar", "transformar", "graficar"))
def test_backends_partial_mantienen_fallo_explicito_en_operaciones_avanzadas(backend, feature):
    salida = _transpilar(HOLOBIT_CASES[feature], backend)
    assert salida.strip()
    assert PARTIAL_ADVANCED_FAILURE_PRIMITIVES[backend][feature] in salida
