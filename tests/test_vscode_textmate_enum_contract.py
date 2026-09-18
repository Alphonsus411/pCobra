import json
import re
from pathlib import Path


GRAMMAR_PATH = (
    Path(__file__).parents[1]
    / "extensions"
    / "vscode"
    / "syntaxes"
    / "cobra.tmLanguage.json"
)


def test_vscode_keyword_pattern_includes_enum_spellings():
    grammar = json.loads(GRAMMAR_PATH.read_text(encoding="utf-8"))
    keyword_patterns = [
        pattern["match"]
        for pattern in grammar["repository"]["keywords"]["patterns"]
        if pattern["name"] == "keyword.control.cobra"
    ]

    assert all(
        any(re.fullmatch(pattern, spelling) for pattern in keyword_patterns)
        for spelling in ("enum", "enumeracion")
    )
