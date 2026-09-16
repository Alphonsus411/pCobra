import pytest
from pygments import lex
from pygments.token import Keyword, Name

from pcobra.cobra.cli.repl.cobra_lexer import CobraLexer


@pytest.mark.parametrize(
    ("source", "expected_token"),
    [
        ("con", Keyword),
        ("como", Keyword),
        ("with", Name),
        ("as", Name),
    ],
)
def test_repl_lexer_follows_con_como_keyword_contract(source, expected_token):
    tokens = [(token, value) for token, value in lex(source, CobraLexer()) if value.strip()]

    assert tokens == [(expected_token, source)]
