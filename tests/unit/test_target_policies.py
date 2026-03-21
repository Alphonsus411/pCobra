import pytest
from argparse import ArgumentTypeError

from pcobra.cobra.cli.target_policies import parse_target, parse_target_list


@pytest.mark.parametrize("value", ["js", "ensamblador", "legacy"])
def test_parse_target_rechaza_aliases_y_valores_no_canonicos(value):
    with pytest.raises(ArgumentTypeError):
        parse_target(value)


def test_parse_target_acepta_nombre_canonico():
    assert parse_target("javascript") == "javascript"


def test_parse_target_list_preserva_javascript_como_unico_nombre_canonico():
    assert parse_target_list("python,javascript") == ["python", "javascript"]


def test_parse_target_list_rechaza_alias_js_en_cualquier_posicion():
    with pytest.raises(ArgumentTypeError):
        parse_target_list("js,python")

    with pytest.raises(ArgumentTypeError):
        parse_target_list("python,js")
