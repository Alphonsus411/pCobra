import pytest
import core.sandbox as sandbox
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


@pytest.mark.timeout(5)
def test_dunder_dict_attr_bloqueado(monkeypatch):
    monkeypatch.setattr("core.sandbox.HAS_RESTRICTED_PYTHON", False, raising=False)
    with pytest.raises(SandboxSecurityError):
        ejecutar_en_sandbox("__builtins__.__dict__")


@pytest.mark.timeout(5)
def test_getattr_dunder_dict_bloqueado(monkeypatch):
    monkeypatch.setattr("core.sandbox.HAS_RESTRICTED_PYTHON", False, raising=False)
    with pytest.raises(SandboxSecurityError):
        ejecutar_en_sandbox("getattr(__builtins__, '__dict__')")


@pytest.mark.timeout(5)
def test_getattr_dunder_dict_subscript_open_bloqueado(monkeypatch):
    monkeypatch.setattr("core.sandbox.HAS_RESTRICTED_PYTHON", False, raising=False)
    with pytest.raises(SandboxSecurityError):
        ejecutar_en_sandbox("getattr(__builtins__, '__dict__')['open']")


@pytest.mark.timeout(5)
def test_vars_builtins_open_bloqueado(monkeypatch):
    monkeypatch.setattr("core.sandbox.HAS_RESTRICTED_PYTHON", False, raising=False)
    with pytest.raises(SandboxSecurityError):
        ejecutar_en_sandbox("vars(__builtins__)['open']")


@pytest.mark.timeout(5)
def test_sin_restrictedpython_falla_sin_fallback_inseguro(monkeypatch):
    monkeypatch.setattr(sandbox, "HAS_RESTRICTED_PYTHON", False)

    def _no_debe_ejecutarse(*_args, **_kwargs):
        raise AssertionError("No debe usarse fallback inseguro por defecto")

    monkeypatch.setattr(sandbox, "_run_in_subprocess", _no_debe_ejecutarse)

    with pytest.raises(RuntimeError, match="sandbox segura requiere RestrictedPython"):
        ejecutar_en_sandbox("print('hola')")


@pytest.mark.timeout(5)
def test_fallback_inseguro_es_explicito(monkeypatch):
    monkeypatch.setattr(sandbox, "HAS_RESTRICTED_PYTHON", False)

    def _fallback(codigo, timeout=None, memoria_mb=None):
        return f"fallback:{codigo}:{timeout}:{memoria_mb}"

    monkeypatch.setattr(sandbox, "_run_in_subprocess", _fallback)

    salida = ejecutar_en_sandbox(
        "print('hola')",
        timeout=2,
        memoria_mb=64,
        allow_insecure_fallback=True,
    )

    assert salida == "fallback:print('hola'):2:64"


@pytest.mark.timeout(5)
def test_syntaxerror_no_usa_fallback_inseguro(monkeypatch):
    monkeypatch.setattr(sandbox, "HAS_RESTRICTED_PYTHON", True)

    def _compilar_con_error(*_args, **_kwargs):
        raise SyntaxError("sintaxis inválida")

    def _no_debe_ejecutarse(*_args, **_kwargs):
        raise AssertionError("No debe ejecutarse fallback ante SyntaxError")

    monkeypatch.setattr(sandbox, "compile_restricted", _compilar_con_error)
    monkeypatch.setattr(sandbox, "_run_in_subprocess", _no_debe_ejecutarse)

    with pytest.raises(SyntaxError, match="sintaxis inválida"):
        ejecutar_en_sandbox("print('hola')")
