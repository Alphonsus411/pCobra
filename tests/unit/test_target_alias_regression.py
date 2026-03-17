from pcobra.cobra.cli.commands.compile_cmd import TRANSPILERS
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, normalize_target_name


def test_js_alias_points_to_javascript_transpiler():
    assert "js" in TRANSPILERS
    assert TRANSPILERS["js"] is TRANSPILERS["javascript"]


def test_official_targets_retains_js_for_cli_compatibility():
    assert "js" in OFFICIAL_TARGETS
    assert normalize_target_name("js") == "javascript"
