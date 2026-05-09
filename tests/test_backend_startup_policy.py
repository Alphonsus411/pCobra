from __future__ import annotations

"""Regresión contractual: política de startup y targets públicos."""

import importlib
import sys

import pytest

LEGACY_TRANSPILER_MODULES = (
    "pcobra.cobra.transpilers.transpiler.to_go",
    "pcobra.cobra.transpilers.transpiler.to_java",
    "pcobra.cobra.transpilers.transpiler.to_cpp",
    "pcobra.cobra.transpilers.transpiler.to_asm",
    "pcobra.cobra.transpilers.transpiler.to_wasm",
)

EXPECTED_PUBLIC_TARGETS = ("python", "javascript", "rust")


@pytest.mark.parity_contract
@pytest.mark.parametrize("module_name", LEGACY_TRANSPILER_MODULES)
def test_runtime_startup_policy_does_not_import_legacy_transpilers(module_name: str) -> None:
    before = set(sys.modules)

    # Startup normal de política contractual (sin resolver transpilers legacy).
    importlib.import_module("pcobra.cobra.architecture.backend_policy")
    importlib.import_module("pcobra.cobra.config.transpile_targets")

    after = set(sys.modules)
    loaded_during_startup = after - before

    assert module_name not in after, f"{module_name} no debe quedar cargado tras startup"
    assert module_name not in loaded_during_startup, (
        f"{module_name} fue cargado durante startup/runtime, violando política pública"
    )


@pytest.mark.parity_contract
@pytest.mark.parametrize("module_name", LEGACY_TRANSPILER_MODULES)
def test_normal_boot_paths_do_not_import_legacy_transpilers(module_name: str) -> None:
    before = set(sys.modules)

    # Rutas normales de arranque: import raíz y bootstrap CLI.
    importlib.import_module("pcobra")
    importlib.import_module("pcobra.cobra.cli.bootstrap")

    after = set(sys.modules)
    loaded_during_boot = after - before

    assert module_name not in after, f"{module_name} no debe quedar cargado tras boot normal"
    assert module_name not in loaded_during_boot, (
        f"{module_name} fue cargado durante boot normal, violando política pública"
    )


@pytest.mark.parity_contract
def test_public_targets_contract_is_exact_in_config_and_architecture() -> None:
    config_targets = importlib.import_module(
        "pcobra.cobra.config.transpile_targets"
    ).OFFICIAL_TARGETS
    public_config_targets = importlib.import_module(
        "pcobra.cobra.config.transpile_targets"
    ).ALLOWED_TARGETS
    policy_targets = importlib.import_module(
        "pcobra.cobra.architecture.backend_policy"
    ).PUBLIC_BACKENDS

    assert config_targets == EXPECTED_PUBLIC_TARGETS
    assert public_config_targets == EXPECTED_PUBLIC_TARGETS
    assert policy_targets == EXPECTED_PUBLIC_TARGETS
    assert config_targets == policy_targets
    assert public_config_targets == policy_targets


@pytest.mark.parity_contract
@pytest.mark.parametrize("invalid_target", ("go", "java", "cpp", "asm", "wasm", "brainfuck"))
def test_non_official_target_fails_with_clear_policy_error(invalid_target: str) -> None:
    assert_public_command_uses_only_public_backends = importlib.import_module(
        "pcobra.cobra.architecture.backend_policy"
    ).assert_public_command_uses_only_public_backends

    with pytest.raises(RuntimeError) as excinfo:
        assert_public_command_uses_only_public_backends(
            command="cobra test-policy",
            targets=(invalid_target,),
        )

    message = str(excinfo.value)
    assert "PUBLIC CONTRACT" in message
    assert "fuera de contrato" in message
    assert "allowed=('python', 'javascript', 'rust')" in message
