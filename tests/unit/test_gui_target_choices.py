from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
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


def test_gui_motor_sugerencias_usa_nombre_canonico_agix():
    from pcobra.gui import runtime

    motor = runtime.MotorIASugerencias(disponible=False)

    assert runtime.CANONICAL_SUGGESTION_ENGINE == "agix"
    assert motor.nombre == "agix"
    assert "agi-core" not in motor.tooltip


def test_gui_runtime_choices_coinciden_con_public_backends(monkeypatch):
    monkeypatch.setattr(
        runtime,
        "require_gui_dependencies",
        lambda: {
            "target_cli_choices": lambda targets: tuple(
                target for target in PUBLIC_BACKENDS if target in targets
            ),
            "OFFICIAL_TARGETS": PUBLIC_BACKENDS,
            "TRANSPILERS": {target: object for target in PUBLIC_BACKENDS},
        },
    )

    assert runtime.gui_target_choices() == PUBLIC_BACKENDS
