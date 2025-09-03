import pytest
from unittest.mock import MagicMock, patch
import pcobra.corelibs as core


def test_obtener_url_sin_whitelist(monkeypatch):
    monkeypatch.delenv("COBRA_HOST_WHITELIST", raising=False)
    with patch("pcobra.corelibs.red.requests.get") as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com")
        mock_get.assert_not_called()


def test_obtener_url_whitelist_vacia(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "")
    with patch("pcobra.corelibs.red.requests.get") as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com")
        mock_get.assert_not_called()


def test_obtener_url_redireccion_http(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(text="ok", url="http://example.com")
    mock_resp.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.get", return_value=mock_resp):
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com", permitir_redirecciones=True)


def test_obtener_url_redireccion_fuera_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(text="ok", url="https://otro.com")
    mock_resp.raise_for_status.return_value = None
    with patch("pcobra.corelibs.red.requests.get", return_value=mock_resp):
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com", permitir_redirecciones=True)
