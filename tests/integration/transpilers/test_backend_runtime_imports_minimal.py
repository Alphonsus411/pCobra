from __future__ import annotations

import pytest

from pcobra.cobra.transpilers.common.utils import get_standard_imports
from tests.integration.transpilers.backend_contracts import generate_code

IMPORT_MARKERS = {
    "python": ("import pcobra.corelibs as _pcobra_corelibs", "import pcobra.standard_library as _pcobra_standard_library"),
    "javascript": (
        "import * as io from './nativos/io.js';",
        "import * as texto from './nativos/texto.js';",
        "import * as interfaz from './nativos/interfaz.js';",
    ),
    "rust": (
        "use crate::corelibs::*;",
        "use crate::standard_library::*;",
        "fn longitud<T: ToString>(valor: T) -> usize {",
    ),
}

CALL_SITE_MARKERS = {
    "python": {"corelibs": "longitud('cobra')", "standard_library": "mostrar('hola')"},
    "javascript": {"corelibs": "longitud('cobra');", "standard_library": "mostrar('hola');"},
    "rust": {"corelibs": 'longitud("cobra");', "standard_library": 'mostrar("hola");'},
}

HOLOBIT_CALL_SITE_MARKERS = {
    "python": "hb = cobra_holobit([1, 2, 3])",
    "javascript": "let hb = cobra_holobit([1, 2, 3]);",
    "rust": "let hb = cobra_holobit(vec![1, 2, 3]);",
}


@pytest.mark.parametrize("backend", tuple(IMPORT_MARKERS))
def test_minimal_runtime_import_markers_are_emitted_per_backend(backend: str):
    generated = generate_code(backend, "corelibs")
    for marker in IMPORT_MARKERS[backend]:
        assert marker in generated


@pytest.mark.parametrize("backend", tuple(IMPORT_MARKERS))
def test_import_bridge_desde_corelibs_y_standard_library_se_inyecta_en_codigo(backend: str):
    generated = generate_code(backend, "corelibs")
    imports = get_standard_imports(backend)
    if isinstance(imports, str):
        imports = [line for line in imports.splitlines() if line.strip()]
    for line in imports:
        assert line in generated


@pytest.mark.parametrize(
    ("backend", "feature"),
    [(backend, feature) for backend in CALL_SITE_MARKERS for feature in ("corelibs", "standard_library")],
)
def test_minimal_runtime_call_sites_are_preserved_per_backend(backend: str, feature: str):
    generated = generate_code(backend, feature)
    assert CALL_SITE_MARKERS[backend][feature] in generated


@pytest.mark.parametrize("backend", tuple(HOLOBIT_CALL_SITE_MARKERS))
def test_minimal_holobit_entrypoint_is_preserved_per_backend(backend: str):
    generated = generate_code(backend, "holobit")
    assert HOLOBIT_CALL_SITE_MARKERS[backend] in generated
