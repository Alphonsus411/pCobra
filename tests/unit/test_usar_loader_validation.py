import pytest

from cobra import usar_loader


@pytest.mark.parametrize("nombre", ["-malicious", "requests==2.0", "../etc/passwd"])
def test_obtener_modulo_rechaza_nombres_invalidos(nombre):
    with pytest.raises(ValueError):
        usar_loader.obtener_modulo(nombre)


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("numpy", ("numpy", "numpy")),
        ("numpy==1.26.4", ("numpy", "numpy==1.26.4")),
        ("numpy>=1.26,<2", ("numpy", "numpy>=1.26,<2")),
    ],
)
def test_parsear_entrada_permite_formato_estricto(monkeypatch, entrada, esperado):
    monkeypatch.delenv("COBRA_USAR_INSTALL_UNSAFE_SPECS", raising=False)
    assert usar_loader._parsear_entrada(entrada) == esperado


@pytest.mark.parametrize(
    "entrada",
    [
        "numpy --index-url https://evil.example/simple",
        "numpy --find-links https://evil.example/wheels",
        "numpy --trusted-host evil.example",
        "https://evil.example/pkg.whl",
        "git+https://evil.example/repo.git",
        "file:///tmp/paquete.whl",
        "numpy @ https://evil.example/pkg.whl",
        "numpy==1.26 --hash=sha256:abc123",
        "numpy #sha256=abc123",
    ],
)
def test_parsear_entrada_rechaza_flags_urls_y_hashes(monkeypatch, entrada):
    monkeypatch.delenv("COBRA_USAR_INSTALL_UNSAFE_SPECS", raising=False)
    with pytest.raises(ValueError):
        usar_loader._parsear_entrada(entrada)
