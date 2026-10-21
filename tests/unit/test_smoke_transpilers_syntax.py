from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace


def _load_smoke_module():
    script_path = Path(__file__).parents[2] / "scripts" / "smoke_transpilers_syntax.py"
    spec = importlib.util.spec_from_file_location(
        "smoke_transpilers_syntax", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_smoke_muestra_los_diagnosticos_del_target_fallido(monkeypatch, capsys):
    from pcobra.cobra.qa import syntax_validation
    from pcobra.cobra.transpilers import registry

    execution = SimpleNamespace(
        has_failures=True,
        report=SimpleNamespace(
            errors_by_target={"rust": ["error[E0308]: tipo inválido"]},
            targets={"rust": SimpleNamespace(ok=2, fail=1, skipped=0)},
        ),
    )
    monkeypatch.setattr(registry, "official_transpiler_targets", lambda: ("rust",))
    monkeypatch.setattr(
        registry, "build_official_transpilers", lambda: {"rust": object}
    )
    monkeypatch.setattr(
        syntax_validation, "execute_syntax_validation", lambda **_: execution
    )

    assert _load_smoke_module().main() == 1

    output = capsys.readouterr().out
    assert "Smoke de transpiladores con fallos" in output
    assert "rust: error[E0308]: tipo inválido" in output
