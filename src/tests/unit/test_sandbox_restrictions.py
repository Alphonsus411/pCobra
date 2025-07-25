import pytest
from backend.src.core.sandbox import ejecutar_en_sandbox


@pytest.mark.timeout(5)
def test_escritura_archivo_bloqueada(tmp_path):
    """`open` no está disponible en `safe_builtins`. Debe lanzar NameError."""
    archivo = tmp_path / "f.txt"
    codigo = f"open({str(archivo)!r}, 'w')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)
    assert not archivo.exists()


@pytest.mark.timeout(5)
def test_borrado_archivo_bloqueado(tmp_path):
    """`__import__('os')` no puede acceder a funciones de borrado."""
    archivo = tmp_path / "f.txt"
    archivo.write_text("hola")
    codigo = f"__import__('os').remove({str(archivo)!r})"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)
    assert archivo.exists()


@pytest.mark.timeout(5)
@pytest.mark.parametrize(
    "codigo",
    [
        "__import__('socket').socket()",
        "__import__('urllib.request')",
    ],
)
def test_red_bloqueada(codigo):
    """Módulos de red no deben poder usarse en la sandbox."""
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)
