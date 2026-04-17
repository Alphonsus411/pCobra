from pcobra.cobra.architecture.backend_policy import INTERNAL_BACKENDS, PUBLIC_BACKENDS
from pcobra.cobra.architecture.unified_ecosystem import (
    IMPORT_POLICY_BLUEPRINT,
    LEGACY_BACKEND_REMOVAL_CANDIDATES,
    OFFICIAL_EXECUTION_BACKENDS,
    OFFICIAL_USER_LANGUAGE,
    build_refactor_workplan,
)


def test_unified_blueprint_keeps_public_contract() -> None:
    assert OFFICIAL_USER_LANGUAGE == "cobra"
    assert OFFICIAL_EXECUTION_BACKENDS == PUBLIC_BACKENDS


def test_legacy_inventory_matches_internal_backends() -> None:
    assert set(LEGACY_BACKEND_REMOVAL_CANDIDATES) == set(INTERNAL_BACKENDS)


def test_refactor_workplan_is_structured() -> None:
    tasks = build_refactor_workplan()
    assert len(tasks) >= 5
    assert tasks[0].id == "T1"
    assert all(task.safe_checks for task in tasks)


def test_import_policy_resolution_order() -> None:
    assert IMPORT_POLICY_BLUEPRINT.resolution_order == (
        "stdlib",
        "project",
        "python_bridge",
        "hybrid",
    )
