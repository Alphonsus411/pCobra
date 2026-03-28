import pytest
from argparse import ArgumentTypeError

from pcobra.cobra.cli.target_policies import parse_target, parse_target_list


@pytest.mark.parametrize("value", ["legacy", "backend_x", "fantasy"])
def test_parse_target_rechaza_valores_fuera_del_set_canonico(value):
    with pytest.raises(ArgumentTypeError):
        parse_target(value)


def test_parse_target_acepta_nombre_canonico():
    assert parse_target("javascript") == "javascript"


def test_parse_target_rechaza_alias_legacy_directamente():
    with pytest.raises(ArgumentTypeError, match="legacy/ambiguo"):
        parse_target("c++")


def test_parse_target_legacy_expone_mensaje_con_migracion_y_version():
    with pytest.raises(ArgumentTypeError) as exc:
        parse_target("js")
    msg = str(exc.value)
    assert "eliminación definitiva en v10.2.0" in msg
    assert "Alternativa recomendada: 'javascript'" in msg


def test_parse_target_list_preserva_nombres_canonicos():
    assert parse_target_list("python,javascript") == ["python", "javascript"]


def test_parse_target_list_rechaza_valores_fuera_del_set_canonico_en_cualquier_posicion():
    with pytest.raises(ArgumentTypeError):
        parse_target_list("fantasy,python")

    with pytest.raises(ArgumentTypeError):
        parse_target_list("python,fantasy")
