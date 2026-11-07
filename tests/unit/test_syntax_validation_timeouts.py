"""Regresión del presupuesto de tiempo del smoke por plataforma."""

from pcobra.cobra.qa import syntax_validation


def test_syntax_tool_timeout_is_extended_only_on_windows(monkeypatch):
    monkeypatch.setattr(syntax_validation.platform, "system", lambda: "Windows")

    assert (
        syntax_validation.syntax_tool_timeout_seconds()
        == syntax_validation.WINDOWS_SYNTAX_TOOL_TIMEOUT_SECONDS
    )


def test_syntax_tool_timeout_uses_default_outside_windows(monkeypatch):
    monkeypatch.setattr(syntax_validation.platform, "system", lambda: "Linux")

    assert (
        syntax_validation.syntax_tool_timeout_seconds()
        == syntax_validation.SYNTAX_TOOL_TIMEOUT_SECONDS
    )
