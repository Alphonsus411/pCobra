from unittest.mock import MagicMock

import pytest

from cobra.cli.cobrahub_client import CobraHubClient


@pytest.mark.timeout(5)
def test_publicar_modulo_cierra_respuesta(tmp_path):
    archivo = tmp_path / "m.co"
    archivo.write_text("var x = 1")

    client = CobraHubClient()
    response = MagicMock()
    response.__enter__.return_value = response
    response.__exit__.side_effect = lambda *args: response.close()
    response.raise_for_status.return_value = None

    client.session.post = MagicMock(return_value=response)

    assert client.publicar_modulo(str(archivo))
    response.close.assert_called_once()
    client.session.post.assert_called_once()


@pytest.mark.timeout(5)
def test_descargar_modulo_cierra_respuesta(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    client = CobraHubClient()
    response = MagicMock()
    response.__enter__.return_value = response
    response.__exit__.side_effect = lambda *args: response.close()
    response.raise_for_status.return_value = None
    response.iter_content.return_value = [b"datos"]
    response.headers = {}

    client.session.get = MagicMock(return_value=response)

    assert client.descargar_modulo("m.co", "out.co")
    response.close.assert_called_once()
    client.session.get.assert_called_once()
