import pytest

from cobra import usar_loader


@pytest.mark.parametrize(
    "nombre",
    ["-malicious", "requests==2.0", "../etc/passwd"],
)
def test_obtener_modulo_rechaza_nombres_invalidos(nombre):
    with pytest.raises(ValueError):
        usar_loader.obtener_modulo(nombre)


@pytest.mark.parametrize(
    "nombre",
    ["pcobra", "corelibs", "standard_library", "backend"],
)
def test_obtener_modulo_rechaza_imports_internos(nombre):
    with pytest.raises(ValueError, match="ruta interna o de backend"):
        usar_loader.obtener_modulo(nombre)


@pytest.mark.parametrize("nombre", ["numpy", "serde", "holobit_sdk"])
def test_obtener_modulo_rechaza_modulos_fuera_allowlist_con_error_estable(nombre):
    with pytest.raises(PermissionError) as exc:
        usar_loader.obtener_modulo(nombre)

    mensaje = str(exc.value)
    assert "Importación no permitida en 'usar'" in mensaje
    assert "Módulos permitidos:" in mensaje
    assert "texto" in mensaje
    assert "holobit" in mensaje


def test_obtener_modulo_rechaza_nombre_no_canonico_node_fetch():
    with pytest.raises(ValueError, match="identificadores simples en minúsculas"):
        usar_loader.obtener_modulo("node-fetch")


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
        "holobit",
    }
