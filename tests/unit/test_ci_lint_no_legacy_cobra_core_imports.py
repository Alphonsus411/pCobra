from __future__ import annotations

from pathlib import Path

from scripts.ci.lint_no_legacy_cobra_core_imports import find_violations


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detecta_import_legacy_pcobra_core_en_cobra_namespace(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "foo.py",
        "from pcobra.core.interpreter import InterpretadorCobra\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "src/pcobra/cobra/foo.py:1" in violations[0]


def test_detecta_import_legacy_core_alias_en_cobra_namespace(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "foo.py",
        "import core.sandbox as sandbox\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "src/pcobra/cobra/foo.py:1" in violations[0]


def test_permite_import_canonico_en_cobra_namespace(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "foo.py",
        "from pcobra.cobra.core.runtime import InterpretadorCobra\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []
