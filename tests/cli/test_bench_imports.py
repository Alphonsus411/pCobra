import builtins
import importlib
import sys
import types

import pytest


BENCH_CMD_MODULE = "pcobra.cobra.cli.commands.bench_cmd"
TARGETS_POLICY_MODULE = "pcobra.cobra.benchmarks.targets_policy"


def _purge_modules(*module_names: str) -> None:
    for module_name in module_names:
        sys.modules.pop(module_name, None)


def test_bench_cmd_import_uses_pcobra_module(monkeypatch):
    _purge_modules(BENCH_CMD_MODULE, TARGETS_POLICY_MODULE)

    attempted_legacy_imports: list[str] = []
    original_import = builtins.__import__

    def tracking_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("scripts.benchmarks"):
            attempted_legacy_imports.append(name)
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", tracking_import)

    bench_cmd = importlib.import_module(BENCH_CMD_MODULE)

    assert attempted_legacy_imports == []
    assert bench_cmd.validate_backend_metadata.__module__ == TARGETS_POLICY_MODULE


def test_targets_policy_tomli_fallback(monkeypatch):
    _purge_modules(TARGETS_POLICY_MODULE, "tomli", "tomllib")

    fake_tomli = types.ModuleType("tomli")
    fake_tomli.loads = lambda *_args, **_kwargs: {}
    monkeypatch.setitem(sys.modules, "tomli", fake_tomli)

    original_import = builtins.__import__

    def without_tomllib(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "tomllib":
            raise ModuleNotFoundError("No module named 'tomllib'", name="tomllib")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", without_tomllib)

    targets_policy = importlib.import_module(TARGETS_POLICY_MODULE)

    assert targets_policy.tomllib is fake_tomli


def test_bench_cmd_missing_dependency_reports_real_module(monkeypatch):
    _purge_modules(BENCH_CMD_MODULE, TARGETS_POLICY_MODULE)

    blocked_module = "pcobra.cobra.cli.target_policies"
    original_import = builtins.__import__

    def block_real_missing_module(name, globals=None, locals=None, fromlist=(), level=0):
        if name == blocked_module:
            raise ModuleNotFoundError(
                f"No module named '{blocked_module}'",
                name=blocked_module,
            )
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", block_real_missing_module)

    with pytest.raises(ModuleNotFoundError) as exc_info:
        importlib.import_module(BENCH_CMD_MODULE)

    assert exc_info.value.name == blocked_module
    assert "scripts.benchmarks.targets_policy" not in str(exc_info.value)
