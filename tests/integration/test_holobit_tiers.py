import pytest

from cobra.cli.commands.compile_cmd import TRANSPILERS
from cobra.core import Lexer, Parser

HOLOBIT_CASES = {
    "graficar": 'var h = holobit([1.0, 2.0, 3.0])\ngraficar(h)\n',
    "proyectar": 'var h = holobit([1.0, 2.0, 3.0])\nproyectar(h, "2D")\n',
    "transformar": 'var h = holobit([1.0, 2.0, 3.0])\ntransformar(h, "rotar", "z", 45)\n',
    "escalar": 'var h = holobit([1.0, 2.0, 3.0])\nescalar(h, 2)\n',
    "mover": 'var h = holobit([1.0, 2.0, 3.0])\nmover(h, 1, 2, 3)\n',
}

SUPPORTED_BY_TIER = {
    "tier1": {
        "graficar": ("python", "js"),
        "proyectar": ("python", "js"),
        "transformar": ("python", "js"),
        "escalar": ("python", "rust", "js"),
        "mover": ("python", "rust", "js"),
    },
    "tier2": {
        "graficar": ("go", "asm"),
        "proyectar": ("go", "asm"),
        "transformar": ("go", "asm"),
        "escalar": ("go", "cpp", "java", "asm"),
        "mover": ("go", "cpp", "java", "asm"),
    },
}


def _transpilar(codigo: str, lang: str) -> str:
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    return TRANSPILERS[lang]().generate_code(ast)


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
