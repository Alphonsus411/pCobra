import importlib
import sys

LEGACY_TRANSPILER_MODULES = (
    "pcobra.cobra.transpilers.transpiler.to_go",
    "pcobra.cobra.transpilers.transpiler.to_cpp",
    "pcobra.cobra.transpilers.transpiler.to_java",
    "pcobra.cobra.transpilers.transpiler.to_wasm",
    "pcobra.cobra.transpilers.transpiler.to_asm",
)


def _purge_modules(prefixes: tuple[str, ...]) -> None:
    for name in list(sys.modules):
        if name.startswith(prefixes):
            sys.modules.pop(name, None)


def test_import_pcobra_no_precarga_transpiladores_legacy():
    _purge_modules(("pcobra", "cobra", "core"))

    importlib.import_module("pcobra")

    for module_name in LEGACY_TRANSPILER_MODULES:
        assert module_name not in sys.modules


def test_import_backend_pipeline_no_precarga_legacy():
    _purge_modules(("pcobra",))

    importlib.import_module("pcobra.cobra.build.backend_pipeline")

    for module_name in LEGACY_TRANSPILER_MODULES:
        assert module_name not in sys.modules


def test_public_backends_permancen_exactamente_tres():
    policy = importlib.import_module("pcobra.cobra.architecture.backend_policy")
    assert policy.PUBLIC_BACKENDS == ("python", "javascript", "rust")
