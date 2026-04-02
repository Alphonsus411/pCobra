from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ci" / "audit_stdlib_parity.py"


def test_audit_stdlib_parity_generates_markdown_report(tmp_path: Path) -> None:
    report = tmp_path / "audit_stdlib_parity_report.md"

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--report", str(report)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    content = report.read_text(encoding="utf-8")
    assert "# Auditoría CI: paridad de `standard_library`" in content
    assert "| funcionalidad | python | javascript | rust | go | cpp | java | wasm | asm |" in content
