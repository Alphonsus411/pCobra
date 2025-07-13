from io import StringIO
from src.cli.cli import main
from src.cobra.transpilers import module_map
import backend.src.cobra.transpilers.module_map as backend_map
import src.core.ast_nodes as src_nodes
import backend.src.core.ast_nodes as backend_nodes
import src.core.interpreter as interpreter_mod


def test_cli_profile_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(backend_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map, "_toml_cache", {}, raising=False)
    monkeypatch.setattr(backend_map, "_toml_cache", {}, raising=False)
    for name in dir(backend_nodes):
        if name.startswith("Nodo"):
            obj = getattr(backend_nodes, name)
            monkeypatch.setattr(src_nodes, name, obj, raising=False)
            monkeypatch.setattr(interpreter_mod, name, obj, raising=False)
    archivo = tmp_path / "prog.co"
    archivo.write_text("imprimir(1)")
    salida = tmp_path / "out.prof"
    main(["profile", str(archivo), "--output", str(salida)])
    assert salida.exists()


def test_cli_profile_shows_stats(tmp_path, monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(backend_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map, "_toml_cache", {}, raising=False)
    monkeypatch.setattr(backend_map, "_toml_cache", {}, raising=False)
    for name in dir(backend_nodes):
        if name.startswith("Nodo"):
            obj = getattr(backend_nodes, name)
            monkeypatch.setattr(src_nodes, name, obj, raising=False)
            monkeypatch.setattr(interpreter_mod, name, obj, raising=False)
    archivo = tmp_path / "prog2.co"
    archivo.write_text("imprimir(2)")
    with StringIO() as buf:
        from unittest.mock import patch
        with patch("sys.stdout", buf):
            main(["profile", str(archivo)])
        data = buf.getvalue()
    assert "ncalls" in data and "tottime" in data


def test_cli_profile_analysis_flag(tmp_path, monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(backend_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map, "_toml_cache", {}, raising=False)
    monkeypatch.setattr(backend_map, "_toml_cache", {}, raising=False)
    for name in dir(backend_nodes):
        if name.startswith("Nodo"):
            obj = getattr(backend_nodes, name)
            monkeypatch.setattr(src_nodes, name, obj, raising=False)
            monkeypatch.setattr(interpreter_mod, name, obj, raising=False)
    archivo = tmp_path / "prog3.co"
    archivo.write_text("imprimir(3)")
    with StringIO() as buf:
        from unittest.mock import patch
        with patch("sys.stdout", buf):
            main(["profile", str(archivo), "--analysis"])
        data = buf.getvalue()
    assert "Lexer profile" in data and "Parser profile" in data
