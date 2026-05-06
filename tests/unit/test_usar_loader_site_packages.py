import pytest

from cobra import usar_loader


@pytest.mark.parametrize("nombre", ["numpy", "node-fetch", "serde", "holobit_sdk"])
def test_rechazo_explicito_modulos_backend_no_canonicos(nombre):
    with pytest.raises(PermissionError, match="backend/no canónico"):
        usar_loader.obtener_modulo(nombre)


@pytest.mark.parametrize("nombre", ["requests", "pandas", "django"])
def test_rechaza_cualquier_modulo_fuera_allowlist(nombre):
    with pytest.raises(PermissionError, match="Módulos permitidos"):
        usar_loader.validar_nombre_modulo_usar(nombre)
