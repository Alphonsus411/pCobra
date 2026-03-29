from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL_WRAPPER = ROOT / "src/cobra/cli/cli.py"
PROXY_WRAPPER = ROOT / "cobra/cli/cli.py"


def _normalize_wrapper_source(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    normalized: list[str] = []
    inside_docstring = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('"""') and stripped.count('"""') >= 2:
            continue
        if stripped.startswith('"""'):
            inside_docstring = not inside_docstring
            continue
        if inside_docstring or not stripped:
            continue
        normalized.append(stripped)

    return "\n".join(normalized)


def test_cli_wrappers_equivalentes_no_divergen() -> None:
    assert _normalize_wrapper_source(CANONICAL_WRAPPER) == _normalize_wrapper_source(
        PROXY_WRAPPER
    )
