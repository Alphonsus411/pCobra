import pytest

from pcobra.cobra.cli.plugin_registry import (
    limpiar_registro,
    obtener_registro,
    obtener_registro_detallado,
    registrar_plugin,
    PluginRegistryError,
)


@pytest.fixture(autouse=True)
def limpiar_antes_y_despues():
    limpiar_registro()
    yield
    limpiar_registro()


@pytest.mark.parametrize("version", ["1.0", "1.2.3", "2.0rc1", "1!2.0", "1.0.post1"])
def test_registrar_plugin_acepta_versiones_pep440(version):
    registrar_plugin("plugin-valido", version, "desc")
    assert obtener_registro()["plugin-valido"] == version


@pytest.mark.parametrize("version", ["", "1..0", "1.0-beta?", "1.0.0.0.0-", "no-es-version"])
def test_registrar_plugin_rechaza_version_invalida(version):
    if version == "":
        with pytest.raises(PluginRegistryError):
            registrar_plugin("plugin-invalido", version)
    else:
        with pytest.raises(ValueError):
            registrar_plugin("plugin-invalido", version)


def test_obtener_registro_detallado_refleja_campos_reales():
    registrar_plugin("plugin-doc", "1.2.3", "descripcion")

    assert obtener_registro() == {"plugin-doc": "1.2.3"}
    assert obtener_registro_detallado() == {
        "plugin-doc": {"version": "1.2.3", "description": "descripcion"}
    }
