from pcobra.gui import runtime


def test_gui_runtime_filtra_targets_fuera_del_conjunto_canonico(monkeypatch):
    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {
            "target_cli_choices": lambda targets: tuple(sorted(targets, reverse=True)),
            "OFFICIAL_TARGETS": ("python", "java", "asm"),
            "TRANSPILERS": {
                "java": object,
                "python": object,
                "backend_x": object,
                "asm": object,
            },
        },
    )

    assert runtime.gui_target_choices() == ("python", "java", "asm")
