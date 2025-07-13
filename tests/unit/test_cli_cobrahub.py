from io import StringIO
from unittest.mock import patch, MagicMock
import pytest

from cli.cli import main
from cli.commands import modules_cmd
from cli import cobrahub_client


@pytest.mark.timeout(5)
def test_cli_modulos_publicar(tmp_path):
    archivo = tmp_path / "m.co"
    archivo.write_text("var x = 1")
    with patch("cli.cobrahub_client.requests.post") as mock_post, \
            patch("sys.stdout", new_callable=StringIO) as out:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp
        main(["modulos", "publicar", str(archivo)])
    assert "Módulo publicado correctamente" in out.getvalue().strip()
    mock_post.assert_called_once()


@pytest.mark.timeout(5)
def test_cli_modulos_buscar(tmp_path, monkeypatch):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text("lock: {}\n")
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", str(mod_file))
    with patch("cli.cobrahub_client.requests.get") as mock_get, \
            patch("sys.stdout", new_callable=StringIO) as out:
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.content = b"data"
        mock_get.return_value = response
        main(["modulos", "buscar", "remote.co"])
    archivo = mods_dir / "remote.co"
    assert archivo.exists()
    assert archivo.read_bytes() == b"data"
    assert f"Módulo descargado en {archivo}" in out.getvalue().strip()
    mock_get.assert_called_once()


@pytest.mark.timeout(5)
def test_publicar_modulo_url_insegura(tmp_path, monkeypatch):
    mod = tmp_path / "m.co"
    mod.write_text("var x = 1")
    monkeypatch.setattr(cobrahub_client, "COBRAHUB_URL", "http://inseguro/api")
    with patch("cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.post") as mock_post:
        ok = cobrahub_client.publicar_modulo(str(mod))
    assert not ok
    err.assert_called_once()
    assert "https://" in err.call_args[0][0]
    mock_post.assert_not_called()


@pytest.mark.timeout(5)
def test_descargar_modulo_url_insegura(tmp_path, monkeypatch):
    destino = tmp_path / "out.co"
    monkeypatch.setattr(cobrahub_client, "COBRAHUB_URL", "http://inseguro/api")
    with patch("cli.cobrahub_client.mostrar_error") as err, \
            patch("cli.cobrahub_client.requests.get") as mock_get:
        ok = cobrahub_client.descargar_modulo("m.co", str(destino))
    assert not ok
    err.assert_called_once()
    assert "https://" in err.call_args[0][0]
    mock_get.assert_not_called()
