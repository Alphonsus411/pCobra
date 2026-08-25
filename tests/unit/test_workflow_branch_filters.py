from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_BRANCHES = ("main", "work")
WORKFLOWS_WITH_BRANCH_FILTERS = (
    ".github/workflows/ci.yml",
    ".github/workflows/runtime-stabilization-contract.yml",
    ".github/workflows/build-binaries.yml",
    ".github/workflows/docker.yml",
    ".github/workflows/pages.yml",
)


def test_workflows_with_branch_filters_target_active_branches():
    for workflow in WORKFLOWS_WITH_BRANCH_FILTERS:
        contenido = (ROOT / workflow).read_text(encoding="utf-8")

        assert "branches:" in contenido, workflow
        assert "master" not in contenido, workflow
        for branch in ACTIVE_BRANCHES:
            assert branch in contenido, workflow
