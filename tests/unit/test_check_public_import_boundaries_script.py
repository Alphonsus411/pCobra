from __future__ import annotations

import ast
import importlib.util
from pathlib import Path


def _load_guard_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "ci" / "check_public_import_boundaries.py"
    spec = importlib.util.spec_from_file_location("check_public_import_boundaries", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_node_import_targets_flags_importfrom_symbol_paths() -> None:
    guard = _load_guard_module()
    node = ast.parse(
        "from pcobra.cobra.cli import internal_compat, helpers\n"
    ).body[0]

    targets = guard._node_import_targets(node)

    assert "pcobra.cobra.cli" in targets
    assert "pcobra.cobra.cli.internal_compat" in targets
    assert "pcobra.cobra.cli.helpers" in targets


def test_node_import_targets_skips_wildcard_suffix_for_importfrom() -> None:
    guard = _load_guard_module()
    node = ast.parse("from pcobra.cobra.cli.internal_compat import *\n").body[0]

    targets = guard._node_import_targets(node)

    assert targets == ["pcobra.cobra.cli.internal_compat"]
