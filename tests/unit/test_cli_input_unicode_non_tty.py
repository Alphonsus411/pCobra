from __future__ import annotations

from types import SimpleNamespace

from pcobra.cobra.cli.cli import CliApplication


def test_leer_input_seguro_en_no_tty_sanea_unicode_mixto(monkeypatch):
    app = CliApplication()
    monkeypatch.setattr("pcobra.cobra.cli.cli.sys.stdin", SimpleNamespace(isatty=lambda: False))
    monkeypatch.setattr("builtins.input", lambda _prompt: "áéíóú 🚀\ud83d")

    saneado = app._leer_input_seguro("prompt> ")

    assert saneado == "áéíóú 🚀�"
    assert all(not (0xD800 <= ord(ch) <= 0xDFFF) for ch in saneado)
    assert saneado.encode("utf-8") == "áéíóú 🚀�".encode("utf-8")
