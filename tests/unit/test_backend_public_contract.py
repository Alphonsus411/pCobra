from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS


def test_politica_publica_exacta_tres_backends():
    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")
