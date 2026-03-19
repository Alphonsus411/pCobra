import importlib


def test_reverse_transpilers_registry_matches_policy_scope():
    reverse_mod = importlib.import_module("pcobra.cobra.transpilers.reverse")

    policy_scope = set(reverse_mod.REVERSE_SCOPE_LANGUAGES)
    registered = set(reverse_mod.REGISTERED_REVERSE_TRANSPILERS.keys())

    assert policy_scope == {"python", "javascript", "java"}
    assert registered.issubset(policy_scope)
    assert "js" not in registered

    assert "ReverseFromPython" in reverse_mod.__all__
    assert "ReverseFromJava" in reverse_mod.__all__
