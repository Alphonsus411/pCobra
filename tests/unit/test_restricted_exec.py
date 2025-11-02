import pytest
from core.sandbox import SandboxSecurityError, ejecutar_en_sandbox


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


@pytest.mark.timeout(5)
def test_exec_bloqueado():
    """Verifica que la función exec está bloqueada en la sandbox."""
    with pytest.raises(Exception):
        ejecutar_en_sandbox("exec('print(1)')")


@pytest.mark.timeout(5)
def test_subprocess_bloqueado():
    """Asegura que no se pueda invocar subprocess dentro de la sandbox."""
    with pytest.raises(Exception):
        ejecutar_en_sandbox("__import__('subprocess').run(['echo', 'hola'])")


@pytest.mark.timeout(5)
def test_import_builtins_open_attr_bloqueado():
    codigo = "__import__('builtins').open"
    with pytest.raises(SandboxSecurityError):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_import_builtins_open_call_bloqueado():
    codigo = "__import__('builtins').open('archivo.txt', 'w')"
    with pytest.raises(SandboxSecurityError):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_getattr_en_builtins_bloqueado():
    codigo = "getattr(__builtins__, 'open')('archivo.txt', 'w')"
    with pytest.raises(SandboxSecurityError):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_subscript_en_builtins_import_bloqueado():
    codigo = "__builtins__.__dict__['__import__']('os')"
    with pytest.raises(SandboxSecurityError):
        ejecutar_en_sandbox(codigo)
