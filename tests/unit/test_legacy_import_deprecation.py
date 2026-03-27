import importlib


def test_legacy_alias_inventory_declara_rutas_canonicas():
    pcobra_pkg = importlib.import_module("pcobra")

    assert pcobra_pkg.LEGACY_IMPORT_ALIAS_INVENTORY == {
        "cobra": "pcobra.cobra",
        "cobra.core": "pcobra.cobra.core",
        "core": "pcobra.core",
    }


def test_legacy_migration_message_incluye_ruta_pcobra():
    pcobra_pkg = importlib.import_module("pcobra")

    mensaje = pcobra_pkg._legacy_migration_message(1)
    assert "pcobra.*" in mensaje
    assert "Fase 1" in mensaje
    assert "Fase 2" in mensaje
    assert "Fase 3" in mensaje
