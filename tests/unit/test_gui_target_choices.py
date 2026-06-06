from pcobra.gui import runtime


def test_gui_runtime_filtra_targets_fuera_del_conjunto_canonico(monkeypatch):
    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {
            "target_cli_choices": lambda targets: tuple(sorted(targets, reverse=True)),
            "OFFICIAL_TARGETS": ("python", "javascript", "rust"),
            "TRANSPILERS": {
                "javascript": object,
                "python": object,
                "backend_x": object,
                "rust": object,
            },
        },
    )

    assert runtime.gui_target_choices() == ("rust", "python", "javascript")
