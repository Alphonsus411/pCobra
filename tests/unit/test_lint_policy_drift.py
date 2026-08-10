from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts import lint_policy_drift


def test_lint_policy_drift_script_passes_on_repo() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "scripts/lint_policy_drift.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_no_confunde_identificador_node_con_target_prohibido(
    tmp_path, monkeypatch
) -> None:
    script = tmp_path / "scripts" / "ci" / "auditor.py"
    script.parent.mkdir(parents=True)
    script.write_text(
        "def targets_from_import(node):\n    return node\n", encoding="utf-8"
    )
    monkeypatch.setattr(lint_policy_drift, "ROOT", tmp_path)

    assert lint_policy_drift._find_policy_drift(script, script.read_text()) == []


def test_no_confunde_node_ids_de_auditoria_con_target_prohibido(
    tmp_path, monkeypatch
) -> None:
    report = tmp_path / "docs" / "auditorias" / "README.md"
    report.parent.mkdir(parents=True)
    report.write_text(
        "Los fallos actuales de targets son los mismos node IDs que en baseline.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(lint_policy_drift, "ROOT", tmp_path)

    assert lint_policy_drift._find_policy_drift(report, report.read_text()) == []


def test_sigue_detectando_target_prohibido_en_literal_python(
    tmp_path, monkeypatch
) -> None:
    script = tmp_path / "scripts" / "config.py"
    script.parent.mkdir(parents=True)
    script.write_text('target = "node"\n', encoding="utf-8")
    monkeypatch.setattr(lint_policy_drift, "ROOT", tmp_path)

    errors = lint_policy_drift._find_policy_drift(script, script.read_text())

    assert len(errors) == 1
    assert "target fuera de policy pública detectado -> node" in errors[0]
