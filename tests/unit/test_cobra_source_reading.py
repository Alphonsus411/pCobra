import logging

from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.services import test_service
from pcobra.cobra.cli.utils.source import read_cobra_source


class _DummyTranspiler:
    def generate_code(self, ast):
        return "generated"


def test_read_cobra_source_normaliza_bom_inicial(tmp_path):
    source = tmp_path / "bom.cobra"
    source.write_text("\ufeffimprimir(1)", encoding="utf-8")

    assert read_cobra_source(source) == "imprimir(1)"


def test_backend_pipeline_build_lee_archivo_antes_de_obtener_ast(monkeypatch, tmp_path):
    source = tmp_path / "main.cobra"
    source.write_text("\ufeffimprimir(1)", encoding="utf-8")
    calls = []

    def fake_read_cobra_source(path):
        calls.append(("read", path))
        return "imprimir(1)"

    def fake_obtener_ast(codigo):
        calls.append(("ast", codigo))
        assert codigo == "imprimir(1)"
        return ["ast"]

    monkeypatch.setattr(backend_pipeline, "read_cobra_source", fake_read_cobra_source)
    monkeypatch.setattr(backend_pipeline, "obtener_ast", fake_obtener_ast)
    monkeypatch.setattr(
        backend_pipeline,
        "resolve_backend_runtime",
        lambda source_file, hints=None: (
            type("Resolution", (), {"backend": "python", "reason": None})(),
            {},
        ),
    )
    monkeypatch.setattr(backend_pipeline, "_official_transpilers", lambda: {"python": _DummyTranspiler})

    result = backend_pipeline.build(str(source), hints={"preferred_backend": "python"})

    assert result["code"] == "generated"
    assert calls == [("read", source), ("ast", "imprimir(1)")]


def test_test_service_read_source_file_usa_read_cobra_source(monkeypatch, tmp_path):
    source = tmp_path / "main.cobra"
    source.write_text("imprimir(1)", encoding="utf-8")
    service = test_service.TestService.__new__(test_service.TestService)
    service._logger = logging.getLogger(__name__)
    calls = []

    def fake_read_cobra_source(path):
        calls.append(path)
        return "imprimir(1)"

    monkeypatch.setattr(test_service, "read_cobra_source", fake_read_cobra_source)

    assert service.read_source_file(str(source)) == "imprimir(1)"
    assert calls == [str(source)]
