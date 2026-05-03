import pytest

from cobra import usar_loader


@pytest.mark.parametrize("nombre", ["numpy", "serde", "holobit_sdk"])
def test_site_packages_no_bypassea_politica_allowlist(nombre):
    with pytest.raises(PermissionError, match="Módulos permitidos"):
        usar_loader.obtener_modulo(nombre)
