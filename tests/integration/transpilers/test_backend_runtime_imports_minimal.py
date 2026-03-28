from __future__ import annotations

import pytest

from pcobra.cobra.transpilers.common.utils import get_standard_imports
from tests.integration.transpilers.backend_contracts import generate_code

IMPORT_MARKERS = {
    "python": ("from corelibs import *", "from standard_library import *"),
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
    "go": ('"cobra/corelibs"', '"cobra/standard_library"'),
    "cpp": ("#include <cobra/corelibs.hpp>", "#include <cobra/standard_library.hpp>"),
    "java": ("import cobra.corelibs.*;", "import cobra.standard_library.*;"),
    "wasm": (
        ";; backend wasm: adaptadores host-managed de corelibs y standard_library",
        '(import "pcobra:corelibs" "longitud"',
        '(import "pcobra:standard_library" "mostrar"',
    ),
    "asm": ("; backend asm: imports de runtime administrados externamente",),
}

CALL_SITE_MARKERS = {
    "python": {"corelibs": "longitud('cobra')", "standard_library": "mostrar('hola')"},
    "javascript": {"corelibs": "longitud('cobra');", "standard_library": "mostrar('hola');"},
    "rust": {"corelibs": 'longitud("cobra");', "standard_library": 'mostrar("hola");'},
    "go": {"corelibs": 'longitud("cobra")', "standard_library": 'mostrar("hola")'},
    "cpp": {"corelibs": 'longitud("cobra");', "standard_library": 'mostrar("hola");'},
    "java": {"corelibs": 'longitud("cobra")', "standard_library": 'mostrar("hola")'},
    "wasm": {"corelibs": "(call $longitud (i32.const 0))", "standard_library": "(call $mostrar (i32.const 0))"},
    "asm": {"corelibs": "CALL longitud 'cobra'", "standard_library": "CALL mostrar 'hola'"},
}

HOLOBIT_CALL_SITE_MARKERS = {
    "python": "hb = cobra_holobit([1, 2, 3])",
    "javascript": "let hb = cobra_holobit([1, 2, 3]);",
    "rust": "let hb = cobra_holobit(vec![1, 2, 3]);",
    "go": "hb := cobra_holobit([]float64{1, 2, 3})",
    "cpp": "auto hb = cobra_holobit({ 1, 2, 3 });",
    "java": "Object hb = cobra_holobit(new double[]{1, 2, 3});",
    "wasm": "(drop (call $cobra_holobit (i32.const 1)))",
    "asm": "HOLOBIT hb [1, 2, 3]",
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
