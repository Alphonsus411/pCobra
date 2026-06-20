from __future__ import annotations

import pytest

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.config.transpile_targets import OFFICIAL_TARGETS
from pcobra.gui.runtime import gui_target_choices
from pcobra.cobra.cli import transpiler_registry as cli_registry
from pcobra.cobra.transpilers import registry as canonical_registry
from pcobra.cobra.transpilers.registry import PUBLIC_TRANSPILER_CLASS_PATHS

EXPECTED_PUBLIC_TARGETS = ("python", "javascript", "rust")
LEGACY_OR_ALIAS_TARGETS = (
    "js",
    "py",
    "node",
    "nodejs",
    "golang",
    "go",
    "java",
    "jvm",
)


class DummyPluginTranspiler:
    def generate_code(self, ast):
        return str(ast)


@pytest.fixture(autouse=True)
def _clean_plugin_state(monkeypatch):
    monkeypatch.setattr(canonical_registry, "_PLUGIN_TRANSPILERS", {})
    monkeypatch.setattr(canonical_registry, "_ENTRYPOINTS_LOADED", False)


def test_cli_wrapper_targets_iguala_contrato_canonico() -> None:
    assert cli_registry.cli_transpiler_targets() == canonical_registry.official_transpiler_targets()


def test_cli_wrapper_transpilers_iguala_claves_y_orden_del_registro_canonico() -> None:
    cli_snapshot = cli_registry.cli_transpilers()
    canonical_snapshot = canonical_registry.get_transpilers(
        include_plugins=True,
        ensure_entrypoints_loaded=True,
    )

    assert tuple(cli_snapshot.keys()) == tuple(canonical_snapshot.keys())


def test_cli_wrapper_transpilers_aplica_mismo_overlay_de_plugins() -> None:
    canonical_registry.register_transpiler_backend(
        "python",
        DummyPluginTranspiler,
        context="tests",
    )

    cli_snapshot = cli_registry.cli_transpilers()
    canonical_snapshot = canonical_registry.get_transpilers(
        include_plugins=True,
        ensure_entrypoints_loaded=True,
    )

    assert cli_snapshot["python"] is DummyPluginTranspiler
    assert canonical_snapshot["python"] is DummyPluginTranspiler
    assert tuple(cli_snapshot.keys()) == tuple(canonical_snapshot.keys())


def test_cli_wrapper_carga_entrypoints_por_contrato_de_get_transpilers(monkeypatch) -> None:
    calls = {"ensure": 0}

    def _fake_ensure() -> None:
        calls["ensure"] += 1

    monkeypatch.setattr(canonical_registry, "ensure_entrypoint_transpilers_loaded_once", _fake_ensure)

    cli_registry.cli_transpilers()

    assert calls["ensure"] == 1


def test_contrato_publico_transpiladores_conserva_solo_targets_oficiales_en_orden() -> None:
    assert OFFICIAL_TARGETS == EXPECTED_PUBLIC_TARGETS
    assert PUBLIC_BACKENDS == EXPECTED_PUBLIC_TARGETS
    assert tuple(PUBLIC_TRANSPILER_CLASS_PATHS.keys()) == EXPECTED_PUBLIC_TARGETS


def test_aliases_legacy_no_aparecen_en_registro_publico_ni_choices_gui() -> None:
    public_registry_targets = tuple(PUBLIC_TRANSPILER_CLASS_PATHS.keys())
    gui_choices = tuple(gui_target_choices())

    assert gui_choices == EXPECTED_PUBLIC_TARGETS
    assert not set(LEGACY_OR_ALIAS_TARGETS).intersection(public_registry_targets)
    assert not set(LEGACY_OR_ALIAS_TARGETS).intersection(gui_choices)
