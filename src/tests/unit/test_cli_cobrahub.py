from io import StringIO
from unittest.mock import patch, MagicMock
import sys
from types import ModuleType
import pytest

dummy = ModuleType("tree_sitter_languages")
dummy.get_parser = lambda *args, **kwargs: None
sys.modules.setdefault("tree_sitter_languages", dummy)

from cli.commands import modules_cmd  # noqa: E402
from cli import cobrahub_client  # noqa: E402


@pytest.mark.timeout(5)
def test_cli_modulos_publicar(tmp_path):
    archivo = tmp_path / "m.co"
    archivo.write_text("var x = 1")
    args = type("obj", (), {"accion": "publicar", "ruta": str(archivo)})
    with patch("cli.cobrahub_client.requests.post") as mock_post, \
            patch("sys.stdout", new_callable=StringIO) as out:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp
        ret = modules_cmd.ModulesCommand().run(args)
    assert ret == 0
    assert "Módulo publicado correctamente" in out.getvalue().strip()
    mock_post.assert_called_once()


@pytest.mark.timeout(5)
def test_cli_modulos_buscar(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", "mods")
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text("lock: {}\n")
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", str(mod_file))
    args = type("obj", (), {"accion": "buscar", "nombre": "remote.co"})
    with patch("cli.cobrahub_client.requests.get") as mock_get, \
            patch("sys.stdout", new_callable=StringIO) as out:
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.content = b"data"
        mock_get.return_value = response
        ret = modules_cmd.ModulesCommand().run(args)
    archivo = mods_dir / "remote.co"
    assert archivo.exists()
    assert archivo.read_bytes() == b"data"
    assert ret == 0
    assert f"Módulo descargado en {archivo}" in out.getvalue().strip()
    mock_get.assert_called_once()


@pytest.mark.timeout(5)
def test_publicar_modulo_url_insegura(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    mod.write_text("var x = 1")
    monkeypatch.setattr(cobrahub_client, "COBRAHUB_URL", "http://inseguro/api")
    with patch("cobra.cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.post") as mock_post:
        ok = cobrahub_client.publicar_modulo(str(mod))
    assert not ok
    err.assert_called_once()
    assert "https://" in err.call_args[0][0]
    mock_post.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_url_insegura(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "out.co"
    monkeypatch.setattr(cobrahub_client, "COBRAHUB_URL", "http://inseguro/api")
    with patch("cobra.cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.get") as mock_get:
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    assert "https://" in err.call_args[0][0]
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_invalida_absoluta(tmp_path):
    destino = tmp_path / "m.co"
    with patch("cobra.cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.get") as mock_get:
        ok = cobrahub_client.descargar_modulo("m.co", str(destino))
    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_invalida_traversal(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "../salir.co"
    with patch("cobra.cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.get") as mock_get:
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_invalida_parent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "../"
    with patch("cobra.cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.get") as mock_get:
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_invalida_tmp_espacios():
    destino = "/tmp/proyecto falso"
    with patch("cobra.cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.get") as mock_get:
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_ruta_valida(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "mods/m.co"
    (tmp_path / "mods").mkdir()
    with patch("cli.cobrahub_client.requests.get") as mock_get:
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.content = b"x"
        mock_get.return_value = resp
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert ok
    archivo = tmp_path / destino
    assert archivo.exists()
    assert archivo.read_bytes() == b"x"
    mock_get.assert_called_once()


@pytest.mark.timeout(5)
def test_publicar_modulo_permission_error(tmp_path):
    archivo = tmp_path / "m.co"
    archivo.write_text("var x = 1")
    with patch("cobra.cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.post") as mock_post, \
            patch("builtins.open", side_effect=PermissionError):
        ok = cobrahub_client.publicar_modulo(str(archivo))
    assert not ok
    err.assert_called_once()
    mock_post.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_permission_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "out.co"
    with patch("cobra.cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.get") as mock_get, \
            patch("builtins.open", side_effect=PermissionError):
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.content = b"data"
        mock_get.return_value = resp
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    mock_get.assert_called_once()


@pytest.mark.timeout(5)
def test_descargar_modulo_symlink(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino_real = tmp_path / "real.co"
    destino_real.write_text("")
    enlace = tmp_path / "link.co"
    enlace.symlink_to(destino_real)
    with patch("cobra.cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.get") as mock_get:
        ok = cobrahub_client.descargar_modulo("m.co", str(enlace))
    assert not ok
    err.assert_called_once()
    mock_get.assert_not_called()


@pytest.mark.timeout(5)
def test_publicar_modulo_host_no_permitido(tmp_path, monkeypatch):
    archivo = tmp_path / "m.co"
    archivo.write_text("var x = 1")
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "cobrahub.example.com")
    monkeypatch.setattr(cobrahub_client, "COBRAHUB_URL", "https://otro.com/api")
    with patch("cobra.cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.post") as mock_post:
        ok = cobrahub_client.publicar_modulo(str(archivo))
    assert not ok
    err.assert_called_once()
    assert "Host" in err.call_args[0][0]
    mock_post.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_host_no_permitido(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    destino = "out.co"
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "cobrahub.example.com")
    monkeypatch.setattr(cobrahub_client, "COBRAHUB_URL", "https://otro.com/api")
    with patch("cobra.cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.get") as mock_get:
        ok = cobrahub_client.descargar_modulo("m.co", destino)
    assert not ok
    err.assert_called_once()
    assert "Host" in err.call_args[0][0]
    mock_get.assert_not_called()
