import pytest

from cobra import usar_loader


@pytest.mark.parametrize(
    "nombre",
    ["-malicious", "requests==2.0", "../etc/passwd", "pcobra", "corelibs_utils"],
)
def test_obtener_modulo_rechaza_nombres_invalidos_o_internos(nombre):
    with pytest.raises(ValueError):
        usar_loader.obtener_modulo(nombre)


def test_obtener_modulo_rechaza_modulos_fuera_allowlist():
    with pytest.raises(PermissionError, match="Importación no permitida"):
        usar_loader.obtener_modulo("numpy")


def test_allowlist_canonica_contiene_modulos_esperados():
    assert usar_loader.USAR_COBRA_ALLOWLIST == {
        "numero",
        "texto",
        "datos",
        "logica",
        "asincrono",
        "sistema",
        "archivo",
        "tiempo",
        "red",
    }
