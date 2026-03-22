from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_validator_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "validate_targets_policy.py"
    spec = importlib.util.spec_from_file_location("validate_targets_policy", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module



def test_iter_scan_files_includes_src_and_tests_and_skips_generated(tmp_path):
    validator = _load_validator_module()

    (tmp_path / "tests" / "utils").mkdir(parents=True)
    (tmp_path / "tests" / "utils" / "ok.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "tests" / "utils" / "__pycache__").mkdir()
    (tmp_path / "tests" / "utils" / "__pycache__" / "generated.py").write_text(
        "print('cached')\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "pcobra" / "cobra" / "cli").mkdir(parents=True)
    (
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "target_policies.py"
    ).write_text("print('ok')\n", encoding="utf-8")

    files = validator.iter_scan_files(tmp_path)
    rel_files = {p.relative_to(tmp_path).as_posix() for p in files}

    assert "src/pcobra/cobra/cli/target_policies.py" in rel_files
    assert "tests/utils/ok.py" in rel_files
    assert "tests/utils/__pycache__/generated.py" not in rel_files



def test_main_detecta_alias_publico_no_canonico(tmp_path, monkeypatch, capsys):
    validator = _load_validator_module()

    (tmp_path / "docs").mkdir(parents=True)
    (tmp_path / "docs" / "guide.md").write_text(
        "Backend recomendado: js\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SCAN_ROOTS", ("docs",))
    monkeypatch.setattr(validator, "PUBLIC_TEXT_PATH_STRS", frozenset({"docs/guide.md"}))

    result = validator.main()

    captured = capsys.readouterr()
    assert result == 1
    assert "alias público no canónico" in captured.err
    assert "docs/guide.md:1" in captured.err
