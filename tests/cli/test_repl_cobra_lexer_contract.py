from pygments import lex
from pygments.token import Keyword, Name, Whitespace

from pcobra.cobra.cli.repl.cobra_lexer import CobraLexer


def test_con_y_como_son_keywords_sin_aliases_en_ingles():
    tokens = [
        (token, value)
        for token, value in lex("con como with as", CobraLexer())
        if token is not Whitespace
    ]

    assert tokens == [
        (Keyword, "con"),
        (Keyword, "como"),
        (Name, "with"),
        (Name, "as"),
    ]
