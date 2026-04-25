from __future__ import annotations

import pytest

from pcobra.cobra.cli import transpiler_registry as cli_registry
from pcobra.cobra.transpilers import registry as canonical_registry


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
