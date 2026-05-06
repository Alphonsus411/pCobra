from pcobra.cobra.usar_loader import obtener_modulo_cobra_oficial


def test_corelibs_all_estable_en_espanol():
    datos = obtener_modulo_cobra_oficial("datos")
    numero = obtener_modulo_cobra_oficial("numero")
    texto = obtener_modulo_cobra_oficial("texto")

    assert "filtrar" in datos.__all__
    assert "mapear" in datos.__all__
    assert "reducir" in datos.__all__

    assert "es_finito" in numero.__all__
    assert "a_snake" in texto.__all__

    assert "isfinite" not in numero.__all__
    assert "snake_case" not in texto.__all__
