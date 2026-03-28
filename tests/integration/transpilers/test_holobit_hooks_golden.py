from __future__ import annotations

from pathlib import Path

import pytest

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from tests.integration.transpilers.backend_contracts import RUNTIME_HOOK_EXPECTATIONS, generate_code

GOLDEN_HOOKS_DIR = Path(__file__).parent / "golden_hooks"


def _extract_hook_signature_lines(generated: str, markers: tuple[str, ...]) -> list[str]:
    lines = generated.splitlines()
    extracted: list[str] = []
    for marker in markers:
        line = next((current for current in lines if marker in current), None)
        assert line is not None, f"No se encontró hook canónico '{marker}' en el código generado"
        extracted.append(line.rstrip())
    return extracted


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_holobit_runtime_hooks_match_golden_snapshots_for_all_official_targets(backend: str):
    generated = generate_code(backend, "proyectar")
    markers = RUNTIME_HOOK_EXPECTATIONS[backend]
    extracted = _extract_hook_signature_lines(generated, markers)

    golden_path = GOLDEN_HOOKS_DIR / f"{backend}.hooks.golden"
    assert golden_path.exists(), f"Falta golden de hooks para backend={backend}: {golden_path}"

    expected = golden_path.read_text(encoding="utf-8").splitlines()
    assert extracted == expected
