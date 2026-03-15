import pytest

from cobra.cli.commands.compile_cmd import TRANSPILERS
from cobra.core import Lexer, Parser
from pcobra.cobra.transpilers.targets import TIER1_TARGETS, TIER2_TARGETS

HOLOBIT_CASES = {
    "holobit": "var h = holobit([1.0, 2.0, 3.0])\n",
    "graficar": 'var h = holobit([1.0, 2.0, 3.0])\ngraficar(h)\n',
    "proyectar": 'var h = holobit([1.0, 2.0, 3.0])\nproyectar(h, "2D")\n',
    "transformar": 'var h = holobit([1.0, 2.0, 3.0])\ntransformar(h, "rotar", "z", 45)\n',
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
        "full": ("python", "javascript"),
        "partial": ("rust", "wasm", "go", "cpp", "java", "asm"),
    },
    "proyectar": {
        "full": ("python", "javascript"),
        "partial": ("rust", "wasm", "go", "cpp", "java", "asm"),
    },
    "transformar": {
        "full": ("python", "javascript"),
        "partial": ("rust", "wasm", "go", "cpp", "java", "asm"),
    },
    "graficar": {
        "full": ("python", "javascript"),
        "partial": ("rust", "wasm", "go", "cpp", "java", "asm"),
    },
    "escalar": {
        "full": ("python", "javascript"),
        "partial": ("rust", "wasm", "go", "cpp", "java", "asm"),
    },
    "mover": {
        "full": ("python", "javascript"),
        "partial": ("rust", "wasm", "go", "cpp", "java", "asm"),
    },
}

FULL_EXPECTATIONS = {
    "python": {
        "holobit": ("from corelibs import *", "from standard_library import *"),
        "proyectar": ("def cobra_proyectar", "proyectar(h"),
        "transformar": ("def cobra_transformar", "transformar(h"),
        "graficar": ("def cobra_graficar", "graficar(h"),
        "escalar": ("escalar(h, 2)",),
        "mover": ("mover(h, 1, 2, 3)",),
    },
    "javascript": {
        "holobit": ("import * as texto from './nativos/texto.js';", "let h ="),
        "proyectar": ("function cobra_proyectar", "cobra_proyectar(h"),
        "transformar": ("function cobra_transformar", "cobra_transformar(h"),
        "graficar": ("function cobra_graficar", "cobra_graficar(h"),
        "escalar": ("escalar(h, 2);",),
        "mover": ("mover(h, 1, 2, 3);",),
    },
}

PARTIAL_FALLBACK_MARKERS = {
    "rust": {
        "holobit": ("NodoHolobit(",),
        "proyectar": ("fn cobra_proyectar",),
        "transformar": ("fn cobra_transformar",),
        "graficar": ("fn cobra_graficar",),
        "escalar": ("escalar(h, 2);",),
        "mover": ("mover(h, 1, 2, 3);",),
    },
    "wasm": {
        "holobit": ("NodoHolobit(",),
        "proyectar": ("(func $cobra_proyectar",),
        "transformar": ("(func $cobra_transformar",),
        "graficar": ("(func $cobra_graficar",),
        "escalar": (";; call escalar",),
        "mover": (";; call mover",),
    },
    "go": {
        "holobit": ("NodoHolobit(",),
        "proyectar": ("func cobraProyectar",),
        "transformar": ("func cobraTransformar",),
        "graficar": ("func cobraGraficar",),
        "escalar": ("escalar(h, 2)",),
        "mover": ("mover(h, 1, 2, 3)",),
    },
    "cpp": {
        "holobit": ("NodoHolobit(",),
        "proyectar": ("inline void cobra_proyectar",),
        "transformar": ("inline void cobra_transformar",),
        "graficar": ("inline void cobra_graficar",),
        "escalar": ("escalar(h, 2);",),
        "mover": ("mover(h, 1, 2, 3);",),
    },
    "java": {
        "holobit": ("NodoHolobit(",),
        "proyectar": ("private static void cobraProyectar",),
        "transformar": ("private static void cobraTransformar",),
        "graficar": ("private static void cobraGraficar",),
        "escalar": ("escalar(h, 2);",),
        "mover": ("mover(h, 1, 2, 3);",),
    },
    "asm": {
        "holobit": ("SET h, h[",),
        "proyectar": ("; Nodo NodoProyectar no soportado",),
        "transformar": ("; Nodo NodoTransformar no soportado",),
        "graficar": ("; Nodo NodoGraficar no soportado",),
        "escalar": ("CALL escalar h, 2",),
        "mover": ("CALL mover h, 1, 2, 3",),
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

    pytest.fail(f"Backend {lang} no clasificado en contrato para primitive {caso}")


@pytest.mark.parametrize("tier", ["tier1", "tier2"])
@pytest.mark.parametrize("caso", HOLOBIT_CASES.keys())
def test_holobit_cobertura_por_tier(tier, caso):
    codigo = HOLOBIT_CASES[caso]
    langs = SUPPORTED_BY_TIER[tier][caso]
    assert langs, f"El caso {caso} debe tener al menos un backend en {tier}"

    for lang in langs:
        salida = _transpilar(codigo, lang)
        assert isinstance(salida, str)
        assert salida.strip()
        _assert_full_or_partial_contract(lang, caso, salida)
