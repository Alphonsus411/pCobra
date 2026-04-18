from __future__ import annotations

from pathlib import Path

from scripts.ci.lint_public_commands_internal_backends import find_violations


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detecta_uso_directo_internal_backends_en_comando_publico(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "foo.py",
        "from pcobra.cobra.architecture.backend_policy import INTERNAL_BACKENDS\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "src/pcobra/cobra/cli/commands/foo.py:1" in violations[0]


def test_permite_comandos_sin_internal_backends(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands_v2" / "ok.py",
        "from pcobra.cobra.cli.internal_compat.legacy_targets import enabled_internal_legacy_targets\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []
