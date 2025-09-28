import importlib
import sqlite3
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import pcobra  # ensure package is initialized
import cobra.cli.cli as cli_module
from cobra.cli.cli import main
from cobra.cli.commands import cache_cmd, modules_cmd
from pcobra.cobra.core import Lexer, Parser


def _reload_ast_cache(monkeypatch):
    monkeypatch.delenv("COBRA_AST_CACHE", raising=False)
    import core.ast_cache as ast_cache_module

    ast_cache_module = importlib.reload(ast_cache_module)
    ast_cache_module.limpiar_cache()
    importlib.reload(cache_cmd)
    return ast_cache_module


@pytest.fixture(autouse=True)
def _stub_gettext(monkeypatch):
    monkeypatch.setattr(cli_module, "setup_gettext", lambda _lang=None: (lambda msg: msg))


def test_cli_help():
    with patch("sys.stdout", new_callable=StringIO) as out:
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0
    assert "uso" in out.getvalue().lower() or "usage" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_modulos_instalar_ruta_no_archivo(tmp_path, monkeypatch):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text("lock: {}\n")
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", str(mod_file))

    ruta = tmp_path / "dir"
    ruta.mkdir()
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "instalar", str(ruta)])
    assert "inv\u00e1lida" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_modulos_instalar_extension_invalida(tmp_path, monkeypatch):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text("lock: {}\n")
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", str(mod_file))

    archivo = tmp_path / "m.txt"
    archivo.write_text("x = 1")
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "instalar", str(archivo)])
    assert "inv\u00e1lida" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_modulos_instalar_enlace_simbolico(tmp_path, monkeypatch):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text("lock: {}\n")
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", str(mod_file))

    real_file = tmp_path / "m.co"
    real_file.write_text("var x = 1")
    link = tmp_path / "link.co"
    link.symlink_to(real_file)
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "instalar", str(link)])
    assert "inv\u00e1lida" in out.getvalue().lower()


def test_cache_command_clears_database(monkeypatch, base_datos_temporal):
    ast_cache_module = _reload_ast_cache(monkeypatch)
    monkeypatch.setattr(Lexer, "tokenizar", lambda self: [])
    monkeypatch.setattr(Parser, "parsear", lambda self: [])

    ast_cache_module.obtener_ast("var cli = 3")

    with sqlite3.connect(base_datos_temporal) as conn:
        before = conn.execute("SELECT COUNT(*) FROM ast_cache").fetchone()[0]
    assert before == 1

    info = []
    errores = []
    monkeypatch.setattr(cache_cmd, "mostrar_info", lambda msg: info.append(msg))
    monkeypatch.setattr(cache_cmd, "mostrar_error", lambda msg: errores.append(msg))
    monkeypatch.setattr(cache_cmd, "_", lambda msg: msg)

    args = SimpleNamespace(vacuum=True)
    resultado = cache_cmd.CacheCommand().run(args)

    assert resultado == 0
    assert info and not errores
    with sqlite3.connect(base_datos_temporal) as conn:
        ast_rows = conn.execute("SELECT COUNT(*) FROM ast_cache").fetchone()[0]
        frag_rows = conn.execute("SELECT COUNT(*) FROM ast_fragments").fetchone()[0]
    assert ast_rows == frag_rows == 0
