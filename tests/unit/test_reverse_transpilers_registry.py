import importlib


def test_reverse_transpilers_registry_matches_policy_scope():
    reverse_mod = importlib.import_module("pcobra.cobra.transpilers.reverse")

    policy_scope = set(reverse_mod.REVERSE_SCOPE_LANGUAGES)
    registered = set(reverse_mod.REGISTERED_REVERSE_TRANSPILERS.keys())

    assert policy_scope == {"python", "javascript", "java"}
    assert registered == policy_scope
    assert "hololang" not in registered
    assert "js" not in registered

    assert "ReverseFromPython" in reverse_mod.__all__
    assert "ReverseFromJava" in reverse_mod.__all__
    assert "ReverseFromHololang" not in reverse_mod.__all__


def test_pcobra_cobra_reverse_no_expone_backend_legacy_experimental():
    reverse_public_mod = importlib.import_module("pcobra.cobra.reverse")

    assert "ReverseFromHololang" not in reverse_public_mod.__all__
    assert "HololangParser" not in reverse_public_mod.__all__
    assert "parse_hololang" not in reverse_public_mod.__all__
    assert not hasattr(reverse_public_mod, "ReverseFromHololang")
    assert not hasattr(reverse_public_mod, "HololangParser")
    assert not hasattr(reverse_public_mod, "parse_hololang")


def test_reverse_policy_modules_no_incluyen_backend_legacy_hololang():
    policy_mod = importlib.import_module("pcobra.cobra.transpilers.reverse.policy")

    assert "hololang" not in policy_mod.REVERSE_SCOPE_LANGUAGES
    assert "hololang" not in policy_mod.REVERSE_SCOPE_MODULES
    assert all("hololang" not in module for module in policy_mod.REVERSE_SCOPE_MODULES.values())


def test_reverse_registry_no_habilita_fallback_legacy_publico_por_defecto():
    reverse_mod = importlib.import_module("pcobra.cobra.transpilers.reverse")

    assert getattr(reverse_mod, "_ALLOW_INTERNAL_LEGACY_FALLBACKS") is False
