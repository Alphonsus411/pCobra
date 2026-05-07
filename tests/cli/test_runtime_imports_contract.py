from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS


def test_cli_import_contract_usa_solo_backends_publicos():
    assert len(PUBLIC_BACKENDS) == 3
    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")
