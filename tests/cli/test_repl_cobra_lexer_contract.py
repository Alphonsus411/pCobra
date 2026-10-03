from pygments import lex
from pygments.token import Keyword, Whitespace

from pcobra.cobra.cli.repl.cobra_lexer import CobraLexer


def test_con_como_y_aliases_en_ingles_son_keywords():
    tokens = [
        (token, value)
        for token, value in lex("con como with as", CobraLexer())
        if token is not Whitespace
    ]

    assert tokens == [
        (Keyword, "con"),
        (Keyword, "como"),
        (Keyword, "with"),
        (Keyword, "as"),
    ]
