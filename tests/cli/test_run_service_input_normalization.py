from pcobra.cobra.cli.services.run_service import _normalizar_codigo_entrada


def test_normalizar_codigo_entrada_remueve_solo_bom_inicial() -> None:
    codigo = "\ufeffimprimir('ok')"
    assert _normalizar_codigo_entrada(codigo) == "imprimir('ok')"


def test_normalizar_codigo_entrada_no_toca_bom_no_inicial() -> None:
    codigo = "imprimir('a')\n\ufeffimprimir('b')"
    assert _normalizar_codigo_entrada(codigo) == codigo

