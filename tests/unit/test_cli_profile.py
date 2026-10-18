from io import StringIO
from cobra.cli.cli import main
from pcobra.cobra.transpilers import module_map


def test_cli_profile_creates_file(tmp_path, monkeypatch):
    from pcobra.cobra.cli.cli import AppConfig
    from pcobra.cobra.cli.commands.profile_cmd import ProfileCommand

    monkeypatch.setenv("COBRA_CLI_COMMAND_PROFILE", "development")
    monkeypatch.setattr(AppConfig, "BASE_COMMAND_CLASSES", [ProfileCommand])
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map, "_toml_cache", {}, raising=False)
    archivo = tmp_path / "prog.co"
    archivo.write_text("imprimir(1)")
    salida = tmp_path / "out.prof"
    assert main(["profile", str(archivo), "--output", str(salida)]) == 0
    assert salida.exists()


def test_cli_profile_shows_stats(tmp_path, monkeypatch):
    from pcobra.cobra.cli.cli import AppConfig
    from pcobra.cobra.cli.commands.profile_cmd import ProfileCommand

    monkeypatch.setenv("COBRA_CLI_COMMAND_PROFILE", "development")
    monkeypatch.setattr(AppConfig, "BASE_COMMAND_CLASSES", [ProfileCommand])
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map, "_toml_cache", {}, raising=False)
    archivo = tmp_path / "prog2.co"
    archivo.write_text("imprimir(2)")
    with StringIO() as buf:
        from unittest.mock import patch

        with patch("sys.stdout", buf):
            assert main(["profile", str(archivo)]) == 0
        data = buf.getvalue()
    assert "ncalls" in data and "tottime" in data


def test_cli_profile_analysis_flag(tmp_path, monkeypatch, caplog):
    from pcobra.cobra.cli.cli import AppConfig
    from pcobra.cobra.cli.commands.profile_cmd import ProfileCommand

    monkeypatch.setenv("COBRA_CLI_COMMAND_PROFILE", "development")
    monkeypatch.setattr(AppConfig, "BASE_COMMAND_CLASSES", [ProfileCommand])
    caplog.set_level("INFO", logger="pcobra.cobra.core.lexer")
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map, "_toml_cache", {}, raising=False)
    archivo = tmp_path / "prog3.co"
    archivo.write_text("imprimir(3)")
    with StringIO() as buf:
        from unittest.mock import patch

        with patch("sys.stdout", buf):
            assert main(["profile", str(archivo), "--analysis"]) == 0
        data = buf.getvalue()
    assert "Lexer profile" in caplog.text
    assert "Parser profile" in data


def test_cli_profile_invalid_ui(tmp_path, monkeypatch):
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map, "_toml_cache", {}, raising=False)
    archivo = tmp_path / "prog4.co"
    archivo.write_text("imprimir(4)")
    with StringIO() as buf:
        from unittest.mock import patch

        with patch("sys.stdout", buf):
            main(["profile", str(archivo), "--ui", "fake_tool"])
        data = buf.getvalue()
    assert "fake_tool" in data and "no encontrada" in data
