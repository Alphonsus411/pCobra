import pytest
from cobra.transpilers import module_map


def test_module_map_rechaza_target_fuera_de_public_backends_en_cobra_toml(tmp_path, monkeypatch):
    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text(
        "[modulos]\n"
        "[modulos.'biblioteca.co']\n"
        "go = 'biblioteca.go'\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("COBRA_TOML", str(toml_file))
    module_map.COBRA_TOML_PATH = str(toml_file)
    module_map._toml_cache = None

    with pytest.raises(ValueError, match="PUBLIC_BACKENDS"):
        module_map.get_toml_map()


def test_module_map_ignora_cobra_mod_para_resolucion(tmp_path, monkeypatch):
    mod = "biblioteca.co"
    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text("[modulos]\n", encoding="utf-8")
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text(
        "[modulos]\n"
        "[modulos.'biblioteca.co']\n"
        "go = 'biblioteca.go'\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("COBRA_TOML", str(toml_file))
    monkeypatch.setenv("COBRA_MODULE_MAP", str(mod_file))
    module_map.COBRA_TOML_PATH = str(toml_file)
    module_map.MODULE_MAP_PATH = str(mod_file)
    module_map._toml_cache = None

    assert module_map.get_mapped_path(mod, "go") == mod


def test_module_map_resuelve_backend_por_contrato_stdlib(tmp_path, monkeypatch):
    contracts_dir = tmp_path / "stdlib_contract"
    contracts_dir.mkdir()
    (contracts_dir / "cobra.web").write_text(
        "public_api=['cobra.web.http']\n"
        "backend_preferido='javascript'\n"
        "fallback_permitido=['python']\n",
        encoding="utf-8",
    )

    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text(
        "[modulos]\n"
        "[modulos.'cobra.web']\n"
        "javascript = 'cobra_web.js'\n"
        "python = 'cobra_web.py'\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(module_map, "STDLIB_CONTRACTS_DIR", str(contracts_dir))
    monkeypatch.setattr(module_map, "COBRA_TOML_PATH", str(toml_file))
    module_map._stdlib_contract_cache = None
    module_map._toml_cache = None

    assert module_map.get_mapped_path("cobra.web", "rust") == "cobra_web.js"
