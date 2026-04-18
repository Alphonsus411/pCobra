from cobra.cli.public_command_policy import (
    PROFILE_DEVELOPMENT,
    PROFILE_PUBLIC,
    filter_legacy_commands_for_profile,
)


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
