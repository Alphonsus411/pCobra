from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ci" / "audit_stdlib_parity.py"


def test_audit_stdlib_parity_generates_markdown_report(tmp_path: Path) -> None:
    report = tmp_path / "audit_stdlib_parity_report.md"
    docs_table = tmp_path / "paridad_stdlib_por_funcion.md"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--report",
            str(report),
            "--docs-table",
            str(docs_table),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + "\n" + result.stderr

    content = report.read_text(encoding="utf-8")
    assert "# Auditoría CI: paridad stdlib por función" in content
    assert "| módulo | función | primario | python | javascript | rust | notas |" in content
    assert "## Estado explícito de `cobra.web`" in content

    docs_content = docs_table.read_text(encoding="utf-8")
    assert "# Paridad de stdlib pública por función" in docs_content
    assert "`src/pcobra/cobra/stdlib_contract/{core,datos,web,system}.py`" in docs_content
