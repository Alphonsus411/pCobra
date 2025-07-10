import pytest
from src.core.sandbox import ejecutar_en_sandbox


@pytest.mark.timeout(5)
def test_eval_bloqueado():
    with pytest.raises(Exception):
        ejecutar_en_sandbox("eval('2+2')")


@pytest.mark.timeout(5)
def test_import_os_system_bloqueado():
    with pytest.raises(Exception):
        ejecutar_en_sandbox("__import__('os').system('echo hola')")


@pytest.mark.timeout(5)
def test_import_os_statement_bloqueado():
    codigo = "import os\nos.system('echo hola')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)
