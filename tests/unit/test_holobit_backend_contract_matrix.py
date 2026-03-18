from __future__ import annotations

import pytest

from pcobra.cobra.transpilers.common.utils import (
    HOOK_SIGNATURE_MARKERS,
    get_runtime_hooks,
    get_standard_imports,
)
from pcobra.cobra.transpilers.compatibility_matrix import (
    BACKEND_COMPATIBILITY,
    COMPATIBILITY_LEVEL_ORDER,
    CONTRACT_FEATURES,
    MIN_REQUIRED_BACKEND_COMPATIBILITY,
    validate_backend_compatibility_contract,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from tests.integration.transpilers.backend_contracts import generate_code


HOLOBIT_FEATURES = CONTRACT_FEATURES[:4]

HOOK_CALL_MARKERS = {
    "python": {
        "holobit": "cobra_holobit([1, 2, 3])",
        "proyectar": "cobra_proyectar(hb, '2d')",
        "transformar": "cobra_transformar(hb, 'rotar', 90)",
        "graficar": "cobra_graficar(hb)",
    },
    "javascript": {
        "holobit": "cobra_holobit([1, 2, 3]);",
        "proyectar": "cobra_proyectar(hb, 2d);",
        "transformar": "cobra_transformar(hb, rotar, 90);",
        "graficar": "cobra_graficar(hb);",
    },
    "rust": {
        "holobit": "cobra_holobit(vec![1, 2, 3]);",
        "proyectar": 'cobra_proyectar(&format!("{}", hb), &format!("{}", 2d));',
        "transformar": 'cobra_transformar(&format!("{}", hb), &format!("{}", rotar), &[]);',
        "graficar": 'cobra_graficar(&format!("{}", hb));',
    },
    "wasm": {
        "holobit": "(drop (call $cobra_holobit (i32.const 1)))",
        "proyectar": "(call $cobra_proyectar (local.get $hb) (i32.const 2d))",
        "transformar": "(call $cobra_transformar (local.get $hb) (i32.const rotar))",
        "graficar": "(call $cobra_graficar (local.get $hb))",
    },
    "go": {
        "holobit": "hb := cobraHolobit([]float64{1, 2, 3})",
        "proyectar": 'cobraProyectar(hb, "2d")',
        "transformar": 'cobraTransformar(hb, "rotar", 90)',
        "graficar": "cobraGraficar(hb)",
    },
    "cpp": {
        "holobit": "auto hb = cobra_holobit({ 1, 2, 3 });",
        "proyectar": "cobra_proyectar(hb, 2d);",
        "transformar": "cobra_transformar(hb, rotar, {});",
        "graficar": "cobra_graficar(hb);",
    },
    "java": {
        "holobit": "Object hb = cobraHolobit(new double[]{1, 2, 3});",
        "proyectar": 'cobraProyectar(hb, "2d");',
        "transformar": 'cobraTransformar(hb, "rotar", 90);',
        "graficar": "cobraGraficar(hb);",
    },
    "asm": {
        "holobit": "HOLOBIT hb [1, 2, 3]",
        "proyectar": "cobra_proyectar:",
        "transformar": "cobra_transformar:",
        "graficar": "cobra_graficar:",
    },
}


def test_compatibility_matrix_matches_minimum_contract():
    validate_backend_compatibility_contract()

    assert set(BACKEND_COMPATIBILITY) == set(OFFICIAL_TARGETS)
    assert set(MIN_REQUIRED_BACKEND_COMPATIBILITY) == set(OFFICIAL_TARGETS)

    for backend in OFFICIAL_TARGETS:
        assert (
            BACKEND_COMPATIBILITY[backend]["tier"]
            == MIN_REQUIRED_BACKEND_COMPATIBILITY[backend]["tier"]
        )
        for feature in CONTRACT_FEATURES:
            actual = BACKEND_COMPATIBILITY[backend][feature]
            minimum = MIN_REQUIRED_BACKEND_COMPATIBILITY[backend][feature]
            assert COMPATIBILITY_LEVEL_ORDER[actual] >= COMPATIBILITY_LEVEL_ORDER[minimum]


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_official_backends_define_standard_imports_and_all_cobra_hooks(backend: str):
    imports = get_standard_imports(backend)
    hooks = get_runtime_hooks(backend)

    if isinstance(imports, str):
        assert imports.strip()
    else:
        assert imports

    assert hooks
    hook_blob = "\n".join(hooks)
    for marker in HOOK_SIGNATURE_MARKERS[backend].values():
        assert marker in hook_blob


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
@pytest.mark.parametrize("feature", HOLOBIT_FEATURES)
def test_codegen_contract_for_cobra_hooks_matches_matrix_level(
    backend: str, feature: str
):
    level = BACKEND_COMPATIBILITY[backend][feature]

    if level == "none":
        with pytest.raises(NotImplementedError):
            generate_code(backend, feature)
        return

    code = generate_code(backend, feature)
    hook_blob = "\n".join(get_runtime_hooks(backend))
    signature = HOOK_SIGNATURE_MARKERS[backend][feature]
    call_marker = HOOK_CALL_MARKERS[backend][feature]

    assert signature in hook_blob
    assert signature in code
    assert call_marker in code

    if level == "full":
        imports = get_standard_imports(backend)
        if isinstance(imports, str):
            for line in imports.splitlines():
                if line.strip():
                    assert line in code
        else:
            for line in imports:
                assert line in code
