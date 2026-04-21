from __future__ import annotations

from pathlib import Path

import pytest

from pcobra.lsp import cobra_plugin


class _DummyDocument:
    def __init__(self, path: Path, source: str) -> None:
        self.path = str(path)
        self.source = source
        self.lines = source.splitlines()


def test_pylsp_format_document_devuelve_edits_si_formatea(monkeypatch, tmp_path):
    archivo = tmp_path / "demo.co"
    archivo.write_text("imprimir(1)\n", encoding="utf-8")
    documento = _DummyDocument(path=archivo, source=archivo.read_text(encoding="utf-8"))

    def _fake_format(path: str) -> bool:
        Path(path).write_text("imprimir(1)\n", encoding="utf-8")
        return True

    monkeypatch.setattr(cobra_plugin, "format_code_with_black", _fake_format)

    edits = cobra_plugin.pylsp_format_document(None, None, documento)

    assert isinstance(edits, list)
    assert edits[0]["newText"] == "imprimir(1)\n"
    assert edits[0]["range"]["start"] == {"line": 0, "character": 0}


def test_pylsp_format_document_lanza_runtimeerror_si_falla_formateo(monkeypatch, tmp_path):
    archivo = tmp_path / "demo.co"
    archivo.write_text("imprimir(1)\n", encoding="utf-8")
    documento = _DummyDocument(path=archivo, source=archivo.read_text(encoding="utf-8"))

    monkeypatch.setattr(cobra_plugin, "format_code_with_black", lambda _path: False)

    with pytest.raises(RuntimeError, match="Fallo de formateo con black"):
        cobra_plugin.pylsp_format_document(None, None, documento)


def test_lsp_plugin_no_depende_de_executecommand():
    assert not hasattr(cobra_plugin, "ExecuteCommand")

