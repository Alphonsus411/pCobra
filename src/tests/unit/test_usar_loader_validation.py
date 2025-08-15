import pytest

from cobra import usar_loader


@pytest.mark.parametrize("nombre", ["-malicious", "requests==2.0", "../etc/passwd"])
def test_obtener_modulo_rechaza_nombres_invalidos(nombre):
    with pytest.raises(ValueError):
        usar_loader.obtener_modulo(nombre)

