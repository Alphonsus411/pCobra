from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_BRANCH = "work"
WORKFLOWS_WITH_BRANCH_FILTERS = (
    ".github/workflows/ci.yml",
    ".github/workflows/runtime-stabilization-contract.yml",
    ".github/workflows/build-binaries.yml",
    ".github/workflows/docker.yml",
    ".github/workflows/pages.yml",
)


def test_workflows_with_branch_filters_target_active_branch_only():
    for workflow in WORKFLOWS_WITH_BRANCH_FILTERS:
        contenido = (ROOT / workflow).read_text(encoding="utf-8")

        assert "branches:" in contenido, workflow
        assert "main" not in contenido, workflow
        assert ACTIVE_BRANCH in contenido, workflow
