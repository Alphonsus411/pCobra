import pytest
from unittest.mock import MagicMock, patch, call
import pcobra.corelibs as core
from pcobra.corelibs import red as red_module


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
    mock_resp = MagicMock(
        status_code=302,
        headers={"Location": "http://example.com"},
        close=MagicMock(),
    )
    with patch("pcobra.corelibs.red.requests.get", return_value=mock_resp) as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com", permitir_redirecciones=True)
        mock_get.assert_called_once_with(
            "https://example.com", timeout=5, allow_redirects=False, stream=True
        )


def test_obtener_url_whitelist_insensible_mayusculas(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "Example.COM")
    mock_resp = MagicMock(url="https://EXAMPLE.com", encoding="utf-8")
    mock_resp.iter_content.return_value = [b"ok"]
    mock_resp.raise_for_status.return_value = None
    mock_resp.status_code = 200
    mock_resp.headers = {}
    with patch("pcobra.corelibs.red.requests.get", return_value=mock_resp) as mock_get:
        assert core.obtener_url("https://EXAMPLE.com") == "ok"
        mock_get.assert_called_once_with(
            "https://EXAMPLE.com", timeout=5, allow_redirects=False, stream=True
        )


def test_obtener_url_redireccion_fuera_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    primer_resp = MagicMock(
        status_code=301,
        headers={"Location": "https://otro.com"},
        close=MagicMock(),
    )
    segunda_resp = MagicMock()
    segunda_resp.close = MagicMock()
    with patch(
        "pcobra.corelibs.red.requests.get",
        side_effect=[primer_resp, segunda_resp],
    ) as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com", permitir_redirecciones=True)
        assert mock_get.call_count == 1


def test_obtener_url_redireccion_permitida(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com,otro.com")
    primer_resp = MagicMock(
        status_code=302,
        headers={"Location": "https://otro.com/destino"},
        close=MagicMock(),
    )
    segunda_resp = MagicMock(
        status_code=200,
        url="https://otro.com/destino",
        headers={},
        encoding="utf-8",
    )
    segunda_resp.iter_content.return_value = [b"contenido"]
    segunda_resp.raise_for_status.return_value = None
    segunda_resp.close = MagicMock()
    with patch(
        "pcobra.corelibs.red.requests.get",
        side_effect=[primer_resp, segunda_resp],
    ) as mock_get:
        resultado = core.obtener_url(
            "https://example.com", permitir_redirecciones=True
        )
        assert resultado == "contenido"
        assert mock_get.call_args_list == [
            call(
                "https://example.com",
                timeout=5,
                allow_redirects=False,
                stream=True,
            ),
            call(
                "https://otro.com/destino",
                timeout=5,
                allow_redirects=False,
                stream=True,
            ),
        ]


def test_enviar_post_redireccion_fuera_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    primer_resp = MagicMock(
        status_code=302,
        headers={"Location": "https://otro.com"},
        close=MagicMock(),
    )
    segunda_resp = MagicMock()
    segunda_resp.close = MagicMock()
    with patch(
        "pcobra.corelibs.red.requests.post",
        side_effect=[primer_resp, segunda_resp],
    ) as mock_post:
        with pytest.raises(ValueError):
            core.enviar_post(
                "https://example.com", {"dato": "valor"}, permitir_redirecciones=True
            )
        assert mock_post.call_count == 1


def test_enviar_post_redireccion_permitida(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com,otro.com")
    primer_resp = MagicMock(
        status_code=307,
        headers={"Location": "https://otro.com/recurso"},
        close=MagicMock(),
    )
    segunda_resp = MagicMock(
        status_code=200,
        url="https://otro.com/recurso",
        headers={},
        encoding="utf-8",
    )
    segunda_resp.iter_content.return_value = [b"ok"]
    segunda_resp.raise_for_status.return_value = None
    segunda_resp.close = MagicMock()
    with patch(
        "pcobra.corelibs.red.requests.post",
        side_effect=[primer_resp, segunda_resp],
    ) as mock_post:
        respuesta = core.enviar_post(
            "https://example.com",
            {"dato": "valor"},
            permitir_redirecciones=True,
        )
        assert respuesta == "ok"
        assert mock_post.call_args_list == [
            call(
                "https://example.com",
                data={"dato": "valor"},
                timeout=5,
                allow_redirects=False,
                stream=True,
            ),
            call(
                "https://otro.com/recurso",
                data={"dato": "valor"},
                timeout=5,
                allow_redirects=False,
                stream=True,
            ),
        ]


def test_enviar_post_demasiadas_redirecciones(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    respuesta_redir = MagicMock(
        status_code=301,
        headers={"Location": "https://example.com"},
        close=MagicMock(),
    )
    with patch(
        "pcobra.corelibs.red.requests.post",
        return_value=respuesta_redir,
    ) as mock_post:
        with pytest.raises(ValueError, match="Demasiadas redirecciones"):
            core.enviar_post(
                "https://example.com",
                {"dato": "valor"},
                permitir_redirecciones=True,
            )
        assert mock_post.call_count == red_module._MAX_REDIRECTS + 1
