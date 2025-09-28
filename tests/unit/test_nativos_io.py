import sys
import sys
from types import ModuleType
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Evita dependencias externas requeridas al importar core.nativos
fake_pybind11 = ModuleType('pybind11')
fake_helpers = ModuleType('pybind11.setup_helpers')
fake_helpers.Pybind11Extension = object
fake_helpers.build_ext = object
sys.modules.setdefault('pybind11', fake_pybind11)
sys.modules.setdefault('pybind11.setup_helpers', fake_helpers)
fake_setuptools = ModuleType('setuptools')
fake_setuptools.Distribution = object
sys.modules.setdefault('setuptools', fake_setuptools)

import core.nativos.io as io


def test_obtener_url_rechaza_esquema_no_http(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch('requests.get') as mock_get:
        with pytest.raises(ValueError):
            io.obtener_url('ftp://ejemplo.com')
        mock_get.assert_not_called()


def test_obtener_url_rechaza_otro_esquema(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch('requests.get') as mock_get:
        with pytest.raises(ValueError):
            io.obtener_url('file:///tmp/archivo.txt')
        mock_get.assert_not_called()


def test_obtener_url_host_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(url="https://example.com", encoding="utf-8")
    mock_resp.iter_content.return_value = [b"ok"]
    mock_resp.raise_for_status.return_value = None
    with patch('requests.get', return_value=mock_resp) as mock_get:
        assert io.obtener_url('https://example.com') == 'ok'
        mock_get.assert_called_once_with('https://example.com', timeout=5, allow_redirects=False, stream=True)


def test_obtener_url_host_whitelist_insensible_mayusculas(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "Example.COM")
    mock_resp = MagicMock(url="https://EXAMPLE.com", encoding="utf-8")
    mock_resp.iter_content.return_value = [b"ok"]
    mock_resp.raise_for_status.return_value = None
    with patch('requests.get', return_value=mock_resp) as mock_get:
        assert io.obtener_url('https://EXAMPLE.com') == 'ok'
        mock_get.assert_called_once_with('https://EXAMPLE.com', timeout=5, allow_redirects=False, stream=True)


def test_obtener_url_sin_whitelist(monkeypatch):
    monkeypatch.delenv("COBRA_HOST_WHITELIST", raising=False)
    with patch('requests.get') as mock_get:
        with pytest.raises(ValueError):
            io.obtener_url('https://example.com')
        mock_get.assert_not_called()


def test_obtener_url_whitelist_vacia(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "")
    with patch('requests.get') as mock_get:
        with pytest.raises(ValueError):
            io.obtener_url('https://example.com')
        mock_get.assert_not_called()


def test_obtener_url_revalida_host_sin_redireccion(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(text="ok", url="https://otro.com")
    mock_resp.raise_for_status.return_value = None
    with patch('requests.get', return_value=mock_resp):
        with pytest.raises(ValueError):
            io.obtener_url('https://example.com')


def test_obtener_url_host_no_permitido(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch('requests.get') as mock_get:
        with pytest.raises(ValueError):
            io.obtener_url('https://otro.com')
        mock_get.assert_not_called()


def test_obtener_url_redireccion_fuera_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    redirect_resp = MagicMock(
        status_code=302,
        headers={"Location": "https://otro.com"},
        url="https://example.com/redirect",
    )
    redirect_resp.iter_content.return_value = []
    with patch('requests.get', return_value=redirect_resp) as mock_get:
        with pytest.raises(ValueError):
            io.obtener_url('https://example.com', permitir_redirecciones=True)
        mock_get.assert_called_once_with(
            'https://example.com', timeout=5, allow_redirects=False, stream=True
        )
    redirect_resp.close.assert_called_once()


def test_obtener_url_redireccion_http(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    redirect_resp = MagicMock(
        status_code=301,
        headers={"Location": "http://example.com"},
        url="https://example.com/redirect",
    )
    redirect_resp.iter_content.return_value = []
    with patch('requests.get', return_value=redirect_resp) as mock_get:
        with pytest.raises(ValueError):
            io.obtener_url('https://example.com', permitir_redirecciones=True)
        mock_get.assert_called_once_with(
            'https://example.com', timeout=5, allow_redirects=False, stream=True
        )
    redirect_resp.close.assert_called_once()


def test_obtener_url_respuesta_muy_grande(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    grande = MagicMock(url="https://example.com", encoding="utf-8")
    grande.iter_content.return_value = [b"a" * (1024 * 1024 + 1)]
    grande.raise_for_status.return_value = None
    with patch('requests.get', return_value=grande):
        with pytest.raises(ValueError):
            io.obtener_url('https://example.com')
    grande.close.assert_called_once()


@pytest.mark.parametrize("func", [io.leer_archivo, lambda p: io.escribir_archivo(p, "dato")])
def test_io_restringe_rutas_absolutas(monkeypatch, tmp_path, func):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    archivo = tmp_path / "interno.txt"
    archivo.write_text("contenido", encoding="utf-8")
    with pytest.raises(ValueError):
        func(str(archivo.resolve()))


@pytest.mark.parametrize("func", [io.leer_archivo, lambda p: io.escribir_archivo(p, "dato")])
def test_io_restringe_rutas_fuera_base(monkeypatch, tmp_path, func):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    externo = tmp_path.parent / "externo.txt"
    externo.write_text("afuera", encoding="utf-8")
    with pytest.raises(ValueError):
        func("../externo.txt")
