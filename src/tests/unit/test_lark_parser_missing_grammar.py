import pytest
from cobra.parser.lark_parser import LarkParser


def test_missing_grammar_file(monkeypatch):
    """Verifica que se emita un mensaje claro si falta la gramática."""

    def fake_open(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr("builtins.open", fake_open)

    mensaje = "No se encuentra el archivo de gramática"
    with pytest.raises(FileNotFoundError, match=mensaje):
        LarkParser([])
