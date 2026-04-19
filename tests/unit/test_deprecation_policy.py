from types import SimpleNamespace

import pytest

import cobra.cli.deprecation_policy as policy


def test_enforce_advanced_profile_phase1_does_not_emit_stdout_warning(monkeypatch, caplog):
    monkeypatch.setenv(policy.DEPRECATION_PHASE_ENV, "1")
    monkeypatch.delenv(policy.LEGACY_TARGETS_MODE_ENV, raising=False)

    stdout_warnings: list[str] = []
    monkeypatch.setattr(policy, "mostrar_advertencia", lambda msg: stdout_warnings.append(msg))

    policy.enforce_advanced_profile_policy(command="bench", args=SimpleNamespace(perfil="publico"))

    assert stdout_warnings == []
    assert "advanced_command_usage" in caplog.text
    assert "--perfil avanzado" in caplog.text


def test_enforce_advanced_profile_phase2_requires_avanzado_or_legacy(monkeypatch):
    monkeypatch.setenv(policy.DEPRECATION_PHASE_ENV, "2")
    monkeypatch.delenv(policy.LEGACY_TARGETS_MODE_ENV, raising=False)

    with pytest.raises(ValueError):
        policy.enforce_advanced_profile_policy(command="bench", args=SimpleNamespace(perfil="publico"))
