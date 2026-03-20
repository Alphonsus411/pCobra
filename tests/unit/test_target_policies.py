import pytest
from argparse import ArgumentTypeError

from pcobra.cobra.cli.target_policies import parse_target


@pytest.mark.parametrize("value", ["js", "ensamblador", "legacy"])
def test_parse_target_rechaza_aliases_y_valores_no_canonicos(value):
    with pytest.raises(ArgumentTypeError):
        parse_target(value)


def test_parse_target_acepta_nombre_canonico():
    assert parse_target("javascript") == "javascript"
