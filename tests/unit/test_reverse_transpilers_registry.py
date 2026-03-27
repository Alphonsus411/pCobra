import importlib


def test_reverse_transpilers_registry_matches_policy_scope():
    reverse_mod = importlib.import_module("pcobra.cobra.transpilers.reverse")

    policy_scope = set(reverse_mod.REVERSE_SCOPE_LANGUAGES)
    registered = set(reverse_mod.REGISTERED_REVERSE_TRANSPILERS.keys())

    assert policy_scope == {"python", "javascript", "java"}
    assert registered == policy_scope
    assert "js" not in registered

    assert "ReverseFromPython" in reverse_mod.__all__
    assert "ReverseFromJava" in reverse_mod.__all__
    assert "ReverseFromJS" in reverse_mod.__all__


def test_pcobra_cobra_reverse_no_expone_backend_legacy_experimental():
    reverse_public_mod = importlib.import_module("pcobra.cobra.reverse")

    assert set(reverse_public_mod.__all__) == {
        "BaseReverseTranspiler",
        "TreeSitterReverseTranspiler",
        "REGISTERED_REVERSE_TRANSPILERS",
        "REVERSE_SCOPE_LANGUAGES",
        "ReverseFromJava",
        "ReverseFromJS",
        "ReverseFromPython",
    }


def test_reverse_policy_modules_solo_incluyen_scope_canonico():
    policy_mod = importlib.import_module("pcobra.cobra.transpilers.reverse.policy")

    assert policy_mod.REVERSE_SCOPE_LANGUAGES == ("python", "javascript", "java")
    assert policy_mod.REVERSE_SCOPE_MODULES == {
        "python": "pcobra.cobra.transpilers.reverse.from_python",
        "javascript": "pcobra.cobra.transpilers.reverse.from_js",
        "java": "pcobra.cobra.transpilers.reverse.from_java",
    }


def test_reverse_registry_no_habilita_fallback_legacy_publico_por_defecto():
    reverse_mod = importlib.import_module("pcobra.cobra.transpilers.reverse")
    assert getattr(reverse_mod, "_LEGACY_IMPORT_PHASE") == 1
    assert getattr(reverse_mod, "_ALLOW_INTERNAL_LEGACY_FALLBACKS") is True
