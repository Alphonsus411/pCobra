from __future__ import annotations

from pcobra.cobra.architecture.backend_policy import (
    INTERNAL_BACKENDS,
    INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW,
)
from pcobra.cobra.architecture.legacy_backend_lifecycle import (
    LEGACY_BACKEND_LIFECYCLE,
    iter_legacy_backend_lifecycle_rows,
    legacy_backend_warning_message,
)
from pcobra.cobra.transpilers.registry import (
    INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS,
    INTERNAL_LEGACY_TRANSPILER_LIFECYCLE_STATUS,
    ordered_internal_legacy_transpiler_entries,
)


def test_lifecycle_metadata_cubre_todos_los_backends_internos():
    assert tuple(LEGACY_BACKEND_LIFECYCLE) == INTERNAL_BACKENDS




def test_retirement_window_usa_calendario_oficial_de_compatibilidad():
    for backend, metadata in LEGACY_BACKEND_LIFECYCLE.items():
        assert metadata.retirement_window == INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW[backend]

def test_registry_internal_legacy_expone_etiqueta_lifecycle_por_backend():
    assert tuple(INTERNAL_LEGACY_TRANSPILER_LIFECYCLE_STATUS) == INTERNAL_BACKENDS
    for backend in INTERNAL_BACKENDS:
        assert backend in INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS
        assert INTERNAL_LEGACY_TRANSPILER_LIFECYCLE_STATUS[backend] in {
            "active-migration",
            "frozen",
            "removal-candidate",
        }


def test_ordered_internal_legacy_entries_incluye_estado():
    entries = ordered_internal_legacy_transpiler_entries()
    assert tuple(entry[0] for entry in entries) == INTERNAL_BACKENDS
    assert all(len(entry) == 3 for entry in entries)


def test_warning_message_usa_formato_unificado():
    msg = legacy_backend_warning_message(target="asm", route="CLI.parse_target")
    assert "ruta no pública" in msg
    assert "estado=removal-candidate" in msg
    assert "fase=phase-1-hide-public-ux" in msg
    assert "ventana=Q3 2026" in msg
    assert "destino público recomendado=python" in msg


def test_iter_rows_respeta_orden_canonic():
    rows = iter_legacy_backend_lifecycle_rows()
    assert tuple(backend for backend, _ in rows) == INTERNAL_BACKENDS


def test_iter_rows_expone_clasificacion_por_fase():
    rows = dict(iter_legacy_backend_lifecycle_rows())
    assert rows["asm"].phase == "phase-1-hide-public-ux"
    assert rows["go"].phase == "phase-2-development-profile-only"
    assert rows["wasm"].retirement_window == "Q2 2027"
