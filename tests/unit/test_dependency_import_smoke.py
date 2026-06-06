from __future__ import annotations

import importlib
import io
import sys

import pytest


def _purge_modules(monkeypatch: pytest.MonkeyPatch, *module_roots: str) -> None:
    """Elimina stubs ya cargados para importar la dependencia real."""

    for name in list(sys.modules):
        if any(name == root or name.startswith(f"{root}.") for root in module_roots):
            monkeypatch.delitem(sys.modules, name, raising=False)


def test_flet_import_and_basic_control_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    _purge_modules(monkeypatch, "flet")

    flet = importlib.import_module("flet")

    text = flet.Text("cobra")
    assert text.value == "cobra"


def test_restrictedpython_import_and_restricted_exec(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _purge_modules(monkeypatch, "RestrictedPython")

    restricted = importlib.import_module("RestrictedPython")

    code = restricted.compile_restricted("resultado = 2 + 3", "<smoke>", "exec")
    namespace = {"__builtins__": restricted.safe_builtins.copy()}
    exec(code, namespace)
    assert namespace["resultado"] == 5


def test_requests_import_and_basic_prepared_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _purge_modules(monkeypatch, "requests")

    requests = importlib.import_module("requests")

    prepared = requests.Request(
        "GET", "https://example.com/recurso", params={"q": "cobra"}
    ).prepare()
    assert prepared.method == "GET"
    assert prepared.url == "https://example.com/recurso?q=cobra"


def test_httpx_import_and_basic_response_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    _purge_modules(monkeypatch, "httpx")

    httpx = importlib.import_module("httpx")

    response = httpx.Response(204)
    assert response.status_code == 204
    assert response.is_success


def test_rich_import_and_basic_console_render(monkeypatch: pytest.MonkeyPatch) -> None:
    _purge_modules(monkeypatch, "rich")

    console_module = importlib.import_module("rich.console")
    table_module = importlib.import_module("rich.table")

    output = io.StringIO()
    console = console_module.Console(file=output, width=40, force_terminal=False)
    table = table_module.Table()
    table.add_column("libreria")
    table.add_row("rich")
    console.print(table)

    assert "rich" in output.getvalue()


def test_openpyxl_optional_extra_import_and_workbook_usage() -> None:
    openpyxl = pytest.importorskip("openpyxl")

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet["A1"] = "cobra"

    assert sheet["A1"].value == "cobra"


def test_pyarrow_optional_extra_import_and_table_usage() -> None:
    pyarrow = pytest.importorskip("pyarrow")

    table = pyarrow.table({"lenguaje": ["cobra"]})

    assert table.num_rows == 1
    assert table.column("lenguaje").to_pylist() == ["cobra"]


def test_packaging_import_and_basic_version_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    _purge_modules(monkeypatch, "packaging")

    version_module = importlib.import_module("packaging.version")

    assert version_module.Version("1.2.3") < version_module.Version("2")


def test_tree_sitter_import_and_basic_parser_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _purge_modules(monkeypatch, "tree_sitter")

    tree_sitter = importlib.import_module("tree_sitter")

    parser = tree_sitter.Parser()
    assert parser is not None
