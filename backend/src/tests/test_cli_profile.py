from io import StringIO
from src.cli.cli import main
from src.cobra.transpilers import module_map


def test_cli_profile_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    archivo = tmp_path / "prog.co"
    archivo.write_text("imprimir(1)")
    salida = tmp_path / "out.prof"
    main(["profile", str(archivo), "--output", str(salida)])
    assert salida.exists()


def test_cli_profile_shows_stats(tmp_path, monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    archivo = tmp_path / "prog2.co"
    archivo.write_text("imprimir(2)")
    with StringIO() as buf:
        from unittest.mock import patch
        with patch("sys.stdout", buf):
            main(["profile", str(archivo)])
        data = buf.getvalue()
    assert "ncalls" in data and "tottime" in data
