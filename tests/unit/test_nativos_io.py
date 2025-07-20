import sys
from types import ModuleType
from pathlib import Path
from unittest.mock import patch
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'backend' / 'src'))

# Evita dependencias externas requeridas al importar src.core.nativos
fake_pybind11 = ModuleType('pybind11')
fake_helpers = ModuleType('pybind11.setup_helpers')
fake_helpers.Pybind11Extension = object
fake_helpers.build_ext = object
sys.modules.setdefault('pybind11', fake_pybind11)
sys.modules.setdefault('pybind11.setup_helpers', fake_helpers)
fake_setuptools = ModuleType('setuptools')
fake_setuptools.Distribution = object
sys.modules.setdefault('setuptools', fake_setuptools)

import src.core.nativos.io as io


def test_obtener_url_rechaza_esquema_no_http():
    with patch('urllib.request.urlopen') as mock_urlopen:
        with pytest.raises(ValueError):
            io.obtener_url('ftp://ejemplo.com')
        mock_urlopen.assert_not_called()
