import pytest

from core.sandbox import SandboxSecurityError, ejecutar_en_sandbox


@pytest.mark.timeout(5)
def test_import_allowlist_permite_math():
    salida = ejecutar_en_sandbox("import math\nprint(math.sqrt(16))")
    assert salida.strip() == "4.0"


@pytest.mark.timeout(5)
def test_import_allowlist_bloquea_modulo_fuera_de_lista():
    with pytest.raises(SandboxSecurityError, match="Importación bloqueada en sandbox"):
        ejecutar_en_sandbox("import os\nprint(os.getcwd())")


@pytest.mark.timeout(5)
def test_import_indirecto_con_dunder_import_respeta_allowlist():
    salida = ejecutar_en_sandbox("m = __import__('math')\nprint(m.factorial(5))")
    assert salida.strip() == "120"


@pytest.mark.timeout(5)
def test_import_indirecto_dunder_import_bloquea_fuera_de_allowlist():
    with pytest.raises(SandboxSecurityError, match="Importación bloqueada en sandbox"):
        ejecutar_en_sandbox("__import__('importlib')")


@pytest.mark.timeout(5)
def test_bloquea_loader_por_nombre_directo():
    with pytest.raises(SandboxSecurityError, match="__loader__"):
        ejecutar_en_sandbox("print(__loader__)")


@pytest.mark.timeout(5)
def test_bloquea_recuperacion_builtins_via_globals():
    codigo = "globals()['__builtins__']['__import__']('math')"
    with pytest.raises(SandboxSecurityError, match="Acceso bloqueado en sandbox"):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_bloquea_import_module_por_reflexion_sin_importlib_explicito():
    codigo = "__import__('math').__loader__.load_module('math')"
    with pytest.raises(SandboxSecurityError, match="Acceso bloqueado en sandbox"):
        ejecutar_en_sandbox(codigo)
