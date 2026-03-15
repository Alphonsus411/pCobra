import pytest
from argparse import ArgumentTypeError

from pcobra.cobra.cli.target_policies import parse_target, set_legacy_target_aliases_enabled


def test_parse_target_rechaza_alias_legacy_por_defecto():
    set_legacy_target_aliases_enabled(False)
    with pytest.raises(ArgumentTypeError):
        parse_target("js")


def test_parse_target_acepta_alias_legacy_con_bandera_temporal():
    set_legacy_target_aliases_enabled(True)
    try:
        assert parse_target("js") == "javascript"
    finally:
        set_legacy_target_aliases_enabled(False)
