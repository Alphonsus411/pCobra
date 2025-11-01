import pytest
from core.sandbox import ejecutar_en_sandbox


@pytest.mark.timeout(5)
def test_operacion_permitida():
    salida = ejecutar_en_sandbox("print(2 + 2)")
    assert salida.strip() == "4"


@pytest.mark.timeout(5)
def test_operacion_bloqueada_open():
    with pytest.raises(Exception):
        ejecutar_en_sandbox("open('archivo.txt', 'w')")


@pytest.mark.timeout(5)
def test_operacion_bloqueada_import():
    codigo = "import os\nos.listdir('.')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_error_sintaxis():
    """Si compile_restricted falla se debe propagar SyntaxError."""
    with pytest.raises(SyntaxError):
        ejecutar_en_sandbox("for")


@pytest.mark.timeout(5)
def test_operacion_bloqueada_alias_prohibido():
    codigo = "from builtins import open as abrir\nabrir('archivo.txt', 'w')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_operacion_bloqueada_io_open():
    codigo = "import io\nio.open('archivo.txt', 'w')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_operacion_bloqueada_io_alias_modulo():
    codigo = "import io as biblioteca\nbiblioteca.open('archivo.txt', 'w')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_operacion_bloqueada_pathlib_path_open():
    codigo = "from pathlib import Path\nPath('archivo.txt').open('w')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)
