from __future__ import annotations

"""Regresión contractual: política de startup y targets públicos."""

import importlib
import sys

import pytest

RETIRED_TRANSPILER_MODULE_PREFIX = "pcobra.cobra.transpilers.transpiler.legacy"
RETIRED_TRANSPILER_MODULES = (
    f"{RETIRED_TRANSPILER_MODULE_PREFIX}.to_go",
    f"{RETIRED_TRANSPILER_MODULE_PREFIX}.to_java",
    f"{RETIRED_TRANSPILER_MODULE_PREFIX}.to_cpp",
    f"{RETIRED_TRANSPILER_MODULE_PREFIX}.to_asm",
    f"{RETIRED_TRANSPILER_MODULE_PREFIX}.to_wasm",
)

EXPECTED_PUBLIC_TARGETS = ("python", "javascript", "rust")


@pytest.mark.parity_contract
@pytest.mark.parametrize("module_name", RETIRED_TRANSPILER_MODULES)
def test_runtime_startup_policy_does_not_import_legacy_transpilers(
    module_name: str,
) -> None:
    before = set(sys.modules)

    # Startup normal de política contractual (sin resolver transpilers legacy).
    importlib.import_module("pcobra.cobra.architecture.backend_policy")
    importlib.import_module("pcobra.cobra.config.transpile_targets")

    after = set(sys.modules)
    loaded_during_startup = after - before

    assert (
        module_name not in after
    ), f"{module_name} no debe quedar cargado tras startup"
    assert (
        module_name not in loaded_during_startup
    ), f"{module_name} fue cargado durante startup/runtime, violando política pública"


@pytest.mark.parity_contract
@pytest.mark.parametrize("module_name", RETIRED_TRANSPILER_MODULES)
def test_normal_boot_paths_do_not_import_legacy_transpilers(module_name: str) -> None:
    before = set(sys.modules)

    # Rutas normales de arranque: import raíz y bootstrap CLI.
    importlib.import_module("pcobra")
    importlib.import_module("pcobra.cobra.cli.bootstrap")

    after = set(sys.modules)
    loaded_during_boot = after - before

    assert (
        module_name not in after
    ), f"{module_name} no debe quedar cargado tras boot normal"
    assert (
        module_name not in loaded_during_boot
    ), f"{module_name} fue cargado durante boot normal, violando política pública"


@pytest.mark.parity_contract
def test_import_pcobra_exposes_lazy_public_api_without_legacy_transpiler_modules() -> (
    None
):
    before = set(sys.modules)

    package = importlib.import_module("pcobra")
    after = set(sys.modules)

    assert "cobra" in package.__all__
    assert "core" in package.__all__
    assert "cli" in package.__all__
    assert "ia" in package.__all__
    assert "jupyter_kernel" in package.__all__
    assert "gui" in package.__all__
    assert "lsp" in package.__all__
    assert "compiler" in package.__all__

    loaded_during_import = after - before
    for module_name in RETIRED_TRANSPILER_MODULES:
        assert module_name not in after
        assert module_name not in loaded_during_import


@pytest.mark.parity_contract
@pytest.mark.parametrize(
    "base_module",
    ("pcobra.__main__", "pcobra.cli", "pcobra.cobra.cli.bootstrap"),
)
def test_base_command_import_paths_do_not_load_legacy_transpilers(
    base_module: str,
) -> None:
    before = set(sys.modules)

    importlib.import_module(base_module)

    after = set(sys.modules)
    loaded_during_import = after - before
    for module_name in RETIRED_TRANSPILER_MODULES:
        assert module_name not in after
        assert module_name not in loaded_during_import


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
@pytest.mark.parametrize(
    "invalid_target", ("go", "java", "cpp", "asm", "wasm", "brainfuck")
)
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


@pytest.mark.parity_contract
def test_legacy_internal_targets_remain_empty_without_architecture_decision() -> None:
    legacy_targets = importlib.import_module(
        "pcobra.cobra.config.transpile_targets"
    ).LEGACY_INTERNAL_TARGETS

    assert legacy_targets == ()


@pytest.mark.parity_contract
def test_public_cli_and_gui_target_surfaces_expose_only_public_backends() -> None:
    public_backends = importlib.import_module(
        "pcobra.cobra.architecture.backend_policy"
    ).PUBLIC_BACKENDS
    cli_registry = importlib.import_module("pcobra.cobra.cli.transpiler_registry")
    target_policies = importlib.import_module("pcobra.cobra.cli.target_policies")
    gui_runtime = importlib.import_module("pcobra.gui.runtime")

    assert cli_registry.cli_transpiler_targets() == public_backends
    assert target_policies.OFFICIAL_TRANSPILATION_TARGETS == public_backends
    assert target_policies.OFFICIAL_RUNTIME_TARGETS == public_backends
    assert target_policies.DOCKER_EXECUTABLE_TARGETS == public_backends
    assert target_policies.VERIFICATION_EXECUTABLE_TARGETS == public_backends

    gui_runtime.require_gui_dependencies.cache_clear()
    try:
        gui_runtime.require_gui_dependencies = lambda: {
            "OFFICIAL_TARGETS": public_backends,
            "TRANSPILERS": {target: object() for target in public_backends},
            "target_cli_choices": lambda targets: tuple(
                target for target in public_backends if target in targets
            ),
        }
        assert gui_runtime.gui_target_choices() == public_backends
    finally:
        importlib.reload(gui_runtime)


@pytest.mark.parity_contract
def test_legacy_syntax_validators_are_not_imported_by_public_runtime_routes() -> None:
    legacy_module = "pcobra.cobra.qa.legacy_syntax_validation"
    sys.modules.pop(legacy_module, None)

    importlib.import_module("pcobra.cobra.qa.syntax_validation")
    importlib.import_module("pcobra.cobra.cli.commands.validar_sintaxis_cmd")
    importlib.import_module("pcobra.cobra.cli.commands.qa_validar_cmd")

    assert legacy_module not in sys.modules


@pytest.mark.parity_contract
def test_transpiler_and_gui_official_targets_match_public_backends_exactly() -> None:
    public_backends = importlib.import_module(
        "pcobra.cobra.architecture.backend_policy"
    ).PUBLIC_BACKENDS
    transpiler_targets = importlib.import_module(
        "pcobra.cobra.transpilers.targets"
    ).OFFICIAL_TARGETS
    gui_deps_targets = importlib.import_module("pcobra.cobra.gui.deps").OFFICIAL_TARGETS

    assert public_backends == EXPECTED_PUBLIC_TARGETS
    assert tuple(transpiler_targets) == public_backends
    assert tuple(gui_deps_targets) == public_backends


@pytest.mark.parity_contract
def test_gui_target_choices_ignores_retired_registered_transpilers() -> None:
    gui_runtime = importlib.import_module("pcobra.gui.runtime")
    public_backends = importlib.import_module(
        "pcobra.cobra.architecture.backend_policy"
    ).PUBLIC_BACKENDS
    retired_targets = ("go", "java", "cpp", "asm", "wasm", "brainfuck")

    gui_runtime.require_gui_dependencies.cache_clear()
    original_require_gui_dependencies = gui_runtime.require_gui_dependencies
    try:
        gui_runtime.require_gui_dependencies = lambda: {
            "OFFICIAL_TARGETS": public_backends,
            "TRANSPILERS": {
                **{target: object() for target in public_backends},
                **{target: object() for target in retired_targets},
            },
            "target_cli_choices": lambda targets: tuple(
                target for target in public_backends if target in targets
            ),
        }

        assert gui_runtime.gui_target_choices() == public_backends
    finally:
        gui_runtime.require_gui_dependencies = original_require_gui_dependencies
        importlib.reload(gui_runtime)


@pytest.mark.parity_contract
def test_gui_target_choices_rejects_official_targets_different_from_public_backends() -> (
    None
):
    gui_runtime = importlib.import_module("pcobra.gui.runtime")
    public_backends = importlib.import_module(
        "pcobra.cobra.architecture.backend_policy"
    ).PUBLIC_BACKENDS

    gui_runtime.require_gui_dependencies.cache_clear()
    original_require_gui_dependencies = gui_runtime.require_gui_dependencies
    try:
        gui_runtime.require_gui_dependencies = lambda: {
            "OFFICIAL_TARGETS": public_backends + ("go",),
            "TRANSPILERS": {target: object() for target in public_backends + ("go",)},
            "target_cli_choices": lambda targets: tuple(targets),
        }

        with pytest.raises(
            RuntimeError, match="OFFICIAL_TARGETS debe coincidir con PUBLIC_BACKENDS"
        ):
            gui_runtime.gui_target_choices()
    finally:
        gui_runtime.require_gui_dependencies = original_require_gui_dependencies
        importlib.reload(gui_runtime)
