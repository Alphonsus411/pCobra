import pytest
from argparse import ArgumentTypeError

from pcobra.cobra.cli.target_policies import parse_target, parse_target_list


@pytest.mark.parametrize("value", ["legacy", "backend_x", "fantasy"])
def test_parse_target_rechaza_valores_fuera_del_set_canonico(value):
    with pytest.raises(ArgumentTypeError):
        parse_target(value)


def test_parse_target_acepta_nombre_canonico():
    assert parse_target("javascript") == "javascript"


def test_parse_target_list_preserva_nombres_canonicos():
    assert parse_target_list("python,javascript") == ["python", "javascript"]


def test_parse_target_list_rechaza_valores_fuera_del_set_canonico_en_cualquier_posicion():
    with pytest.raises(ArgumentTypeError):
        parse_target_list("fantasy,python")

    with pytest.raises(ArgumentTypeError):
        parse_target_list("python,fantasy")
