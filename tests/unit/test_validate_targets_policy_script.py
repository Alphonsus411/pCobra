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

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "ok.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "ok_test.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "tests" / "__pycache__").mkdir()
    (tmp_path / "tests" / "__pycache__" / "generated.py").write_text("kot" "lin\n", encoding="utf-8")

    files = validator.iter_scan_files(tmp_path)
    rel_files = {p.relative_to(tmp_path).as_posix() for p in files}

    assert "src/ok.py" in rel_files
    assert "tests/ok_test.py" in rel_files
    assert "tests/__pycache__/generated.py" not in rel_files


def test_main_detects_out_of_policy_terms_in_src_and_tests(tmp_path, monkeypatch, capsys):
    validator = _load_validator_module()

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "module.py").write_text("# backend " + "kot" + "lin\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_policy.py").write_text("# mention " + "swi" + "ft\n", encoding="utf-8")

    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SCAN_ROOTS", ("src", "tests"))

    result = validator.main()

    captured = capsys.readouterr()
    assert result == 1
    assert "src/module.py:1" in captured.err
    assert "tests/test_policy.py:1" in captured.err
