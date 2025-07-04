import shutil
import subprocess
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.core.sandbox import ejecutar_en_sandbox_js


@pytest.mark.timeout(5)
def test_sandbox_js_template_string():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    salida = ejecutar_en_sandbox_js("console.log(`hola ${1 + 1}`)")
    assert salida.strip() == "hola 2"


@pytest.mark.timeout(5)
def test_sandbox_js_inyeccion_no_ejecuta():
    if not shutil.which("node"):
        pytest.skip("node no disponible")
    codigo = "`);console.log('inseguro');//"
    with pytest.raises(subprocess.CalledProcessError) as exc:
        ejecutar_en_sandbox_js(codigo)
    assert "inseguro" not in exc.value.stdout
