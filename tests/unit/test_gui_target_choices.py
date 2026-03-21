from pcobra.gui import app, idle


def test_gui_app_filtra_targets_fuera_del_conjunto_canonico(monkeypatch):
    monkeypatch.setattr(
        app,
        "TRANSPILERS",
        {
            "java": object,
            "python": object,
            "backend_x": object,
            "asm": object,
        },
    )

    assert app._gui_target_choices() == ("python", "java", "asm")


def test_gui_idle_filtra_targets_fuera_del_conjunto_canonico(monkeypatch):
    monkeypatch.setattr(
        idle,
        "TRANSPILERS",
        {
            "rust": object,
            "backend_x": object,
            "javascript": object,
            "cpp": object,
        },
    )

    assert idle._gui_target_choices() == ("rust", "javascript", "cpp")
