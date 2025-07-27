import shutil
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.sandbox import (
    ejecutar_en_sandbox_js,
    compilar_en_sandbox_cpp,
    ejecutar_en_contenedor,
)


@pytest.mark.timeout(5)
def test_js_timeout_invalido():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    salida = ejecutar_en_sandbox_js("console.log('hola')", timeout=-1)
    assert "agotado" in salida


@pytest.mark.timeout(5)
def test_compilar_cpp_sin_contenedor():
    with patch("core.sandbox.ejecutar_en_contenedor", side_effect=RuntimeError("docker")):
        with pytest.raises(RuntimeError, match="Contenedor.*C\+\+"):
            compilar_en_sandbox_cpp("int main() { return 0; }")


def test_contenedor_backend_invalido():
    with pytest.raises(ValueError):
        ejecutar_en_contenedor("print(1)", "malicioso")
