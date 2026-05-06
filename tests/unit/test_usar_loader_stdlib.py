import pytest

from cobra import usar_loader


@pytest.mark.parametrize("nombre", ["numero", "texto", "datos", "holobit"])
def test_entrypoint_obtener_modulo_delega_en_obtener_modulo_cobra_oficial(monkeypatch, nombre):
    llamado = {"nombre": None}

    def _fake_oficial(n):
        llamado["nombre"] = n
        return object()

    monkeypatch.setattr(usar_loader, "obtener_modulo_cobra_oficial", _fake_oficial)
    assert usar_loader.obtener_modulo(nombre) is not None
    assert llamado["nombre"] == nombre


@pytest.mark.parametrize(
    "nombre",
    [
        "pcobra.core.database",
        "cobra.usar_loader",
        "corelibs.numero",
        "standard_library.texto",
        "backend_python",
    ],
)
def test_rechaza_rutas_internas_y_backend(nombre):
    with pytest.raises((ValueError, PermissionError), match="(usar|backend|interna|permitida)"):
        usar_loader.validar_nombre_modulo_usar(nombre)
