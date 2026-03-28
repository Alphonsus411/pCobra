from __future__ import annotations

from pathlib import Path

from scripts.audit_retired_targets import run_audit


def test_audit_retired_targets_detecta_alias_y_legacy(tmp_path: Path):
    (tmp_path / "README.md").write_text(
        "cobra compilar hola.co --backend c++\n"
        "cobra compilar hola.co --backend js\n",
        encoding="utf-8",
    )

    findings = run_audit(tmp_path, globs=("*.md",))

    assert len(findings) == 2
    matched = {item.matched.lower() for item in findings}
    assert matched == {"c++", "js"}
    recommendations = {item.recommendation for item in findings}
    assert "cpp" in recommendations
    assert "javascript" in recommendations

