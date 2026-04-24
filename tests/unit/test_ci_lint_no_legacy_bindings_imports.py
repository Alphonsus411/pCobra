from __future__ import annotations

from pathlib import Path

from scripts.ci.lint_no_legacy_bindings_imports import find_violations


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detecta_import_legacy_bindings_en_src_pcobra(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "foo.py",
        "from bindings.contract import resolve_binding\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "src/pcobra/cobra/foo.py:1" in violations[0]


def test_permite_import_canonico_pcobra_bindings(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "foo.py",
        "from pcobra.cobra.bindings.contract import resolve_binding\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []
