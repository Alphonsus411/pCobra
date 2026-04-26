from cobra.cli.public_command_policy import (
    PROFILE_DEVELOPMENT,
    PROFILE_PUBLIC,
    PUBLIC_COMMANDS_CONTRACT,
    filter_commands_for_profile,
    filter_legacy_commands_for_profile,
)


def test_filter_commands_publico_permite_solo_superficie_v2_publica():
    visibles = filter_commands_for_profile(
        ("run", "build", "test", "mod", "repl", "interactive", "legacy", "debug"),
        PROFILE_PUBLIC,
    )
    assert visibles == {"run", "build", "test", "mod", "repl"}


def test_filter_commands_development_permite_toda_superficie_v2():
    comandos = ("run", "build", "test", "mod", "repl", "legacy", "debug")
    visibles = filter_commands_for_profile(comandos, PROFILE_DEVELOPMENT)
    assert visibles == set(comandos)


def test_public_commands_contract_oficial_v2_no_incluye_alias_legacy():
    assert PUBLIC_COMMANDS_CONTRACT == ("run", "build", "test", "mod", "repl")
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
