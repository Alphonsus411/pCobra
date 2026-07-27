import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcobra.core.lexer import Lexer
from pcobra.core.parser import Parser
from pcobra.cobra.transpilers.registry import get_transpilers

from tests.utils.runtime import execute_transpiled_code
from tests.utils.targets import BEST_EFFORT_INTERNAL_RUNTIME_TARGETS, OFFICIAL_RUNTIME_TARGETS

TRANSPILERS = get_transpilers()


def _collect_output_differences(tmp_path, archivo, esperados, *, langs, allow_experimental=False):
    tokens = Lexer(archivo.read_text()).analizar_token()
    ast = Parser(tokens).parsear()

    diferencias = {}
    for lang in langs:
        if lang not in esperados:
            continue
        transpiler = TRANSPILERS[lang]()
        if lang == "python":
            transpiler.codigo = ""
        try:
            codigo = transpiler.generate_code(ast)
        except NotImplementedError as e:
            diferencias[lang] = f"Error: {e}"
            continue
        try:
            salida = execute_transpiled_code(
                lang,
                codigo,
                tmp_path,
                allow_experimental=allow_experimental,
            )
        except pytest.skip.Exception:
            continue
        except Exception as e:  # pylint: disable=broad-except
            diferencias[lang] = f"Error: {e}"
            continue
        if salida != esperados[lang]:
            diferencias[lang] = salida
    return diferencias


def test_cross_backend_output(tmp_path, transpiler_case):
    """Compara únicamente los runtimes oficiales equivalentes entre backends."""
    archivo, esperados = transpiler_case

    diferencias = _collect_output_differences(
        tmp_path,
        archivo,
        esperados,
        langs=OFFICIAL_RUNTIME_TARGETS,
    )
    assert not diferencias, f"Salidas distintas: {diferencias}"


@pytest.mark.experimental
def test_cross_backend_output_experimental_best_effort(tmp_path, transpiler_case):
    """Go/Java se validan aparte como cobertura experimental, no contractual."""
    archivo, esperados = transpiler_case

    diferencias = _collect_output_differences(
        tmp_path,
        archivo,
        esperados,
        langs=BEST_EFFORT_INTERNAL_RUNTIME_TARGETS,
        allow_experimental=True,
    )
    assert not diferencias, f"Salidas experimentales distintas: {diferencias}"
