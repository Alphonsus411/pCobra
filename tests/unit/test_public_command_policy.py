from cobra.cli.public_command_policy import (
    PROFILE_DEVELOPMENT,
    PROFILE_PUBLIC,
    PUBLIC_COMMANDS_CONTRACT,
    filter_commands_for_profile,
    filter_legacy_commands_for_profile,
    is_public_v2_hidden_compat_command,
    is_public_v2_visible_command,
    registered_commands_for_profile,
    visible_commands_for_profile,
)


def test_filter_commands_publico_permite_solo_superficie_v2_publica():
    visibles = filter_commands_for_profile(
        (
            "run",
            "build",
            "test",
            "mod",
            "repl",
            "gui",
            "paquete",
            "hub",
            "interactive",
            "legacy",
            "debug",
        ),
        PROFILE_PUBLIC,
    )
    assert visibles == {"run", "build", "test", "mod", "repl", "gui"}


def test_capas_publicas_v2_separan_visibles_de_registrados():
    comandos = ("run", "build", "paquete", "hub", "installer")

    assert visible_commands_for_profile(comandos, PROFILE_PUBLIC) == {"run", "build"}
    assert registered_commands_for_profile(comandos, PROFILE_PUBLIC) == {
        "run",
        "build",
        "paquete",
        "hub",
    }
    assert is_public_v2_visible_command("run") is True
    assert is_public_v2_visible_command("paquete") is False
    assert is_public_v2_hidden_compat_command("paquete") is True
    assert is_public_v2_hidden_compat_command("installer") is False


def test_filter_commands_development_permite_toda_superficie_v2():
    comandos = (
        "run",
        "build",
        "test",
        "mod",
        "repl",
        "legacy",
        "debug",
        "installer",
        "paquete",
        "hub",
    )
    visibles = filter_commands_for_profile(comandos, PROFILE_DEVELOPMENT)
    assert visibles == set(comandos)


def test_public_commands_contract_oficial_v2_no_incluye_alias_legacy():
    assert PUBLIC_COMMANDS_CONTRACT == (
        "run",
        "build",
        "test",
        "mod",
        "repl",
        "gui",
    )
    assert "interactive" not in PUBLIC_COMMANDS_CONTRACT


def test_filter_legacy_commands_publico_bloquea_toda_superficie_v1():
    visibles = filter_legacy_commands_for_profile(
        ("interactive", "ejecutar", "docs"),
        PROFILE_PUBLIC,
    )
    assert visibles == set()


def test_filter_legacy_commands_development_permite_superficie_v1_para_migracion():
    comandos = ("interactive", "ejecutar", "docs")
    visibles = filter_legacy_commands_for_profile(comandos, PROFILE_DEVELOPMENT)
    assert visibles == set(comandos)
