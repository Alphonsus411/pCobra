from io import StringIO
from unittest.mock import patch, MagicMock
import pytest

from src.cli.cli import main
from src.cli.commands import modules_cmd


@pytest.mark.timeout(5)
def test_cli_modulos_publicar(tmp_path):
    archivo = tmp_path / "m.co"
    archivo.write_text("var x = 1")
    with patch("src.cli.cobrahub_client.requests.post") as mock_post, \
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
    with patch("src.cli.cobrahub_client.requests.get") as mock_get, \
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
