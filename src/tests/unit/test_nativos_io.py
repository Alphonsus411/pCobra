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


def test_obtener_url_rechaza_esquema_no_http():
    with patch('requests.get') as mock_get:
        with pytest.raises(ValueError):
            io.obtener_url('ftp://ejemplo.com')
        mock_get.assert_not_called()


def test_obtener_url_rechaza_otro_esquema():
    with patch('requests.get') as mock_get:
        with pytest.raises(ValueError):
            io.obtener_url('file:///tmp/archivo.txt')
        mock_get.assert_not_called()


def test_obtener_url_host_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock()
    mock_resp.text = "ok"
    mock_resp.raise_for_status.return_value = None
    with patch('requests.get', return_value=mock_resp) as mock_get:
        assert io.obtener_url('https://example.com') == 'ok'
        mock_get.assert_called_once_with('https://example.com', timeout=5, allow_redirects=False)


def test_obtener_url_host_no_permitido(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch('requests.get') as mock_get:
        with pytest.raises(ValueError):
            io.obtener_url('https://otro.com')
        mock_get.assert_not_called()


def test_obtener_url_redireccion_fuera_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(text="ok", url="https://otro.com")
    mock_resp.raise_for_status.return_value = None
    with patch('requests.get', return_value=mock_resp):
        with pytest.raises(ValueError):
            io.obtener_url('https://example.com', permitir_redirecciones=True)


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
